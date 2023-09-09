from projects.utils.diff_match_patch import get_diff_match_patch
from channels.generic.websocket import AsyncWebsocketConsumer
from projects.utils import content_differences
from projects.utils.locks import get_locks
from django.conf import settings
from projects import models
import aiofiles
import asyncio
import json
import os

class FileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        file_pk = self.scope["url_route"]["kwargs"]["file_pk"]
        file_consumer_pk = self.scope["url_route"]["kwargs"]["file_consumer_pk"]

        self.file = await models.File.objects.filter(pk=file_pk).select_related("project").afirst()
        self.file_consumer = await models.FileConsumer.objects.filter(pk=file_consumer_pk).afirst()  # TODO: user, project, file match

        if not self.file or not self.file_consumer:
            await self.close()
            return

        self.dmp = get_diff_match_patch()

        locks = get_locks()

        self.file_lock = locks.get(f"file_lock_{self.file.pk}", None)
        self.patch_file_lock = locks.get(f"file_lock_{self.file.pk}.patch", None)

        if not self.file_lock:
            self.file_lock = asyncio.Lock()
            locks[f"file_lock_{self.file.pk}"] = self.file_lock

        if not self.patch_file_lock:
            self.patch_file_lock = asyncio.Lock()
            locks[f"file_lock_{self.file.pk}.patch"] = self.patch_file_lock

        await self.accept()

    async def disconnect(self, code: int):
        pass

    async def receive(self, text_data: str = None, bytes_data: bytes = None):
        text_data_json = json.loads(text_data)
        client_differences_stack = content_differences.parse_differences_stack(text_data_json["differences_stack"])

        if (self.file_consumer.shadow["server_version"] == text_data_json["server_version"]) or ((self.file_consumer.shadow["server_version"] != text_data_json["server_version"]) and (self.file_consumer.backup_shadow["server_version"] == text_data_json["server_version"])):  # TODO: no need for the second statement

            if self.file_consumer.shadow["server_version"] != text_data_json["server_version"]:
                self.file_consumer.shadow["content"] = self.file_consumer.backup_shadow["content"]
                self.file_consumer.shadow["server_version"] = self.file_consumer.backup_shadow["server_version"]

            patches_stack = []
            applied_patches_stack = []
            client_version = self.file_consumer.shadow["client_version"]
            shadow_content = self.file_consumer.shadow["content"]

            while str(client_version) in client_differences_stack:
                client_differences = client_differences_stack[str(client_version)]
                if content_differences.differences_contain_changes(differences=client_differences):  # TODO: necessary?
                    patches = self.dmp.patch_make(a=client_differences)
                    patches_stack.append(patches)
                    shadow_content, _ = self.dmp.patch_apply(
                        patches=patches, text=shadow_content
                    )
                client_version += 1

            self.file_consumer.shadow["content"] = shadow_content
            self.file_consumer.shadow["client_version"] = client_version
            self.file_consumer.backup_shadow["content"] = shadow_content
            self.file_consumer.backup_shadow["server_version"] = self.file_consumer.shadow["server_version"]

            async with self.file_lock:
                async with aiofiles.open(
                    file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(self.file.project.pk), str(self.file.pk)), mode="r+"
                ) as file:
                    file_content = await file.read()
                    if patches_stack:
                        while patches_stack:
                            patches = patches_stack.pop(0)
                            file_content, results = self.dmp.patch_apply(
                                patches=patches, text=file_content
                            )
                            applied_patches = [patches[i] for i in range(0, len(patches)) if results[i]]
                            applied_patches_stack.append(applied_patches)
                        await file.seek(0)
                        await file.write(file_content)
                        await file.truncate()

            if applied_patches_stack:
                async with self.patch_file_lock:
                    async with aiofiles.open(
                        file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(self.file.project.pk), f"{self.file.pk}.patch"), mode="a"
                    ) as file:
                        patches_text = ""
                        while applied_patches_stack:
                            patches_text += self.dmp.patch_toText(patches=applied_patches_stack.pop(0))
                        await file.write(patches_text)

            server_differences = self.dmp.diff_main(
                text1=self.file_consumer.shadow["content"], text2=file_content
            )
            server_differences_stack = {str(self.file_consumer.shadow["server_version"]): server_differences}
            server_differences_stack = content_differences.serialize_differences_stack(differences_stack=server_differences_stack)

            self.file_consumer.shadow["content"] = file_content
            self.file_consumer.shadow["server_version"] += 1

            await self.file_consumer.asave(update_fields=["shadow", "backup_shadow"])

            text_data = json.dumps({
                "differences_stack": server_differences_stack,
                "client_version": self.file_consumer.shadow["client_version"],
            })
            await self.send(text_data=text_data)

        else: await self.close()  # server_version(s) do not match!
