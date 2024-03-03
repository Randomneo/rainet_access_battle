from typing import Protocol


class IOHandler(Protocol):
    async def send(self, message: str) -> None: ...
    async def read(self) -> str: ...
    async def send_board(self, board_state: str) -> None: ...


class CliHandler:
    async def send(self, message: str) -> None:
        print(message)

    async def read(self) -> str:
        return input()

    async def send_board(self, board_state: str) -> None:
        print(CliHandler.make_cli_board(board_state))

    @staticmethod
    def make_cli_board(pieces: str) -> str:
        rows: list[list[str | None]] = [[None]*8 for _ in range(8)]
        for piece in pieces.split(';'):
            piece_type, pos_x, pos_y = piece.split(',')
            rows[int(pos_y)][int(pos_x)] = piece_type[0]

        result = '*---'*9 + '*\n'
        for i, row in enumerate(rows):
            result += (
                f'| {7 - i} | '
                + ' | '.join(item or ' ' for item in row)
                + ' |\n'
            )
            result += '*---'*9 + '*\n'

        result += (
            '|y/x|'
            + ' |'.join(f' {item}' for item in range(8))
            + ' |\n'
        )
        result += '*---'*9 + '*\n'
        return result
