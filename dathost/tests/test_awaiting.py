import asynctest

from secrets import token_urlsafe

from ..models.account import AccountModel
from ..models.server import ServerModel
from ..models.file import FileModel
from ..models.backup import BackupModel
from ..models.metrics import MetricsModel, MapsModel, PlayerModel, \
    PlayersOnlineGraphModel
from ..models.match import MatchModel, TeamModel, MatchPlayerModel

from ..server.awaiting.backup import AwaitingBackup
from ..server.awaiting.file import AwaitingFile

from ..match.awaiting import AwaitingMatch

from ..server.awaiting import ServerAwaiting

from .. import Awaiting

from ..settings import ServerSettings, MatchSettings

from .shared_vars import EMAIL, PASSWORD, TEST_IMAGE_DIRETORY


class TestAwaitingClient(asynctest.TestCase):
    use_default_loop = True

    async def setUp(self):
        self.client = Awaiting(
            email=EMAIL,
            password=PASSWORD
        )

    async def tearDown(self):
        await self.client.close()

    async def test_account(self):
        account = await self.client.account()

        self.assertTrue(isinstance(account, AccountModel))

    async def test_domains(self):
        async for domain in self.client.domains():
            self.assertTrue(type(domain) == str)

    async def test_context(self):
        context = Awaiting(EMAIL, PASSWORD)

        async with context as client:
            await client.account()

        async with context as client:
            async for domain in client.domains():
                pass

    async def test_list_servers(self):
        async for data, server in self.client.servers():
            self.assertIsInstance(data, ServerModel)
            self.assertIsInstance(server, ServerAwaiting)

    async def test_server_csgo(self):
        server_data, server = await self.client.create_server(
            ServerSettings(
                name="Awaiting CS: GO server",
                location="sydney",
            ).csgo(
                slots=5,
                game_token="",
                tickrate=128,
                rcon_password=token_urlsafe()
            )
        )

        self.assertIsInstance(server_data, ServerModel)
        self.assertIsInstance(server, ServerAwaiting)

        self.assertIsInstance(await server.get(), ServerModel)

        await server.console_send("status")
        await server.console_retrive()

        await server.start()
        await server.stop()
        await server.reset()

        await server.update(
            ServerSettings(
                name="Renamed Awaiting CS: GO server",
                location="sydney"
            ).csgo(
                slots=7
            )
        )

        async for data, f in server.files():
            self.assertIsInstance(data, FileModel)
            self.assertIsInstance(f, AwaitingFile)

        async for data, f in server.files(hide_default=True, file_sizes=True):
            self.assertIsInstance(data, FileModel)
            self.assertIsInstance(f, AwaitingFile)

        async for data, backup in server.backups():
            self.assertIsInstance(data, BackupModel)
            self.assertIsInstance(backup, AwaitingBackup)

            await backup.restore()

        metrics = await server.metrics()
        self.assertIsInstance(metrics, MetricsModel)

        for map_ in metrics.maps():
            self.assertIsInstance(map_, MapsModel)

        for player in metrics.players_online():
            self.assertIsInstance(player, PlayerModel)

        for player in metrics.all_time_players():
            self.assertIsInstance(player, PlayerModel)

        for player in metrics.players_online_graph():
            self.assertIsInstance(player, PlayersOnlineGraphModel)

        await server.ftp_reset()

        test_1_file = server.file("test.txt")
        await test_1_file.upload(b"hello world")
        await test_1_file.move("cfg")

        self.assertTrue(type(await test_1_file.dowload()) == bytes)

        self.assertIsNone(await test_1_file.delete())

        test_2_file = server.file("test.jpg")
        await test_2_file.upload_file(TEST_IMAGE_DIRETORY)
        await test_2_file.save(TEST_IMAGE_DIRETORY)

        async for data in test_2_file.download_iterate():
            self.assertTrue(type(data) == bytes)

        self.assertIsNone(await test_2_file.delete())

        _, duplicate = await server.duplicate(sync=True)
        self.assertIsNone(await duplicate.delete())

        match_data, match = await server.create_match(
            MatchSettings(
            ).team_1(
                [
                    "[U:1:116962485]",
                    76561198017567105,
                    "STEAM_0:1:186064092"
                ]
            ).team_2(
                [
                    "[U:1:320762620]",
                    "STEAM_0:1:83437164",
                    76561198214871324
                ]
            )
        )

        self.assertIsInstance(match_data, MatchModel)
        self.assertIsInstance(match, AwaitingMatch)

        self.assertIsInstance(await match.get(), MatchModel)

        self.assertIsInstance(match_data.team_1, TeamModel)
        self.assertIsInstance(match_data.team_2, TeamModel)

        for player in match_data.players():
            self.assertIsInstance(player, MatchPlayerModel)

        self.assertIsNone(await server.delete())

    async def test_server_mumble(self):
        data, server = await self.client.create_server(
            ServerSettings(
                name="Blocking Mumble server",
                location="sydney"
            ).mumble(
                slots=7,
                superuser_password=token_urlsafe()
            )
        )

        self.assertIsInstance(data, ServerModel)
        self.assertIsInstance(server, ServerAwaiting)

        self.assertIsInstance(await server.get(), ServerModel)

        self.assertIsNone(await server.delete())

    async def test_server_tf2(self):
        data, server = await self.client.create_server(
            ServerSettings(
                name="Awaiting TF2 server",
                location="sydney"
            ).tf2(
                slots=5,
                rcon_password=token_urlsafe()
            )
        )

        self.assertIsInstance(data, ServerModel)
        self.assertIsInstance(server, ServerAwaiting)

        self.assertIsInstance(await server.get(), ServerModel)

        await server.update(
            ServerSettings(
                name="Renamed Awaiting CS: GO server",
                location="sydney"
            ).csgo(
                slots=7
            )
        )

        self.assertIsNone(await server.delete())

    async def test_server_teamspeak(self):
        data, server = await self.client.create_server(
            ServerSettings(
                name="Blocking TF2 server",
                location="sydney"
            ).teamspeak(
                slots=5,
            )
        )

        self.assertIsInstance(data, ServerModel)
        self.assertIsInstance(server, ServerAwaiting)

        self.assertIsInstance(await server.get(), ServerModel)

        self.assertIsNone(await server.delete())
