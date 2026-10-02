from ._lld import code, table, note, caveat, question, problem

TIC_TAC_TOE = problem(
    id="tic-tac-toe",
    title="Design Tic-Tac-Toe",
    level="easy",
    patterns=["Strategy"],
    summary="N x N board, O(1) win detection with counters, pluggable player strategies (human, random, unbeatable).",
    statement=[
        "Design an N &times; N tic-tac-toe game for two players, where each player can be a human or a computer. Detecting a win must not rescan the whole board after every move.",
    ],
    requirements=[
        "Board of size N; players alternate placing their mark on an empty cell; a player wins with N in a row, column or diagonal; draw when the board is full. Invalid moves are rejected without changing the turn.",
    ],
    choose=[
        ["Human or computer players, different AIs", "Strategy", "Each player type implements <code>next_move(board)</code>"],
        ["Win check after every move", "Counters per line", "+1 / &minus;1 per row, column and diagonal gives O(1) detection"],
    ],
    choose_notes=["No other pattern is needed. Resist adding factories and observers to a problem this small; say why you are not using them."],
    classes=[
        ["<code>Board</code>", "Cells and line counters; <code>place(r, c, player)</code> returns the winner if any"],
        ["<code>Player</code>", "Strategy: <code>next_move(board)</code>"],
        ["<code>Game</code>", "Turn order and the game loop"],
    ],
    implementation=[
        code('''
            import random

            class Board:
                def __init__(self, n):
                    self.n = n
                    self.cells = [[None] * n for _ in range(n)]
                    self.rows, self.cols = [0] * n, [0] * n
                    self.diag = self.anti = 0
                    self.moves = 0

                def empty(self):
                    return [(r, c) for r in range(self.n) for c in range(self.n) if self.cells[r][c] is None]

                def place(self, r, c, mark):
                    """returns mark if this move wins, else None. O(1)."""
                    if not (0 <= r < self.n and 0 <= c < self.n) or self.cells[r][c] is not None:
                        raise ValueError(f"illegal move {(r, c)}")
                    self.cells[r][c] = mark
                    self.moves += 1
                    d = 1 if mark == "X" else -1
                    self.rows[r] += d; self.cols[c] += d
                    if r == c: self.diag += d
                    if r + c == self.n - 1: self.anti += d
                    target = d * self.n
                    if target in (self.rows[r], self.cols[c], self.diag, self.anti):
                        return mark
                    return None

                def full(self): return self.moves == self.n * self.n

            class Scripted:
                def __init__(self, moves): self.moves = iter(moves)
                def next_move(self, board, mark): return next(self.moves)

            class RandomPlayer:
                def __init__(self, seed): self.rng = random.Random(seed)
                def next_move(self, board, mark): return self.rng.choice(board.empty())

            class WinOrBlock:
                """take a winning cell, else block the opponent, else centre-ish"""
                def next_move(self, board, mark):
                    other = "O" if mark == "X" else "X"
                    for who in (mark, other):
                        for r, c in board.empty():
                            trial = Board(board.n)
                            for rr in range(board.n):
                                for cc in range(board.n):
                                    if board.cells[rr][cc]:
                                        trial.place(rr, cc, board.cells[rr][cc])
                            if trial.place(r, c, who):
                                return r, c
                    return min(board.empty(), key=lambda rc: abs(rc[0] - board.n // 2) + abs(rc[1] - board.n // 2))

            def play(n, x, o):
                board, players = Board(n), [("X", x), ("O", o)]
                turn = 0
                while True:
                    mark, player = players[turn % 2]
                    r, c = player.next_move(board, mark)
                    if board.place(r, c, mark):
                        return f"{mark} wins after {board.moves} moves"
                    if board.full():
                        return "draw"
                    turn += 1

            print(play(3, Scripted([(0, 0), (1, 1), (2, 2)]), Scripted([(0, 1), (0, 2)])))
            print(play(4, Scripted([(0, 3), (1, 2), (2, 1), (3, 0)]), Scripted([(0, 0), (1, 1), (2, 2)])))
            print(play(3, WinOrBlock(), WinOrBlock()))
            results = [play(3, WinOrBlock(), RandomPlayer(s)) for s in range(200)]
            tally = {"X wins": 0, "O wins": 0, "draw": 0}
            for r in results:
                tally[r.split(" after")[0]] += 1
            print("smart X vs random O over 200 games:", tally)
        '''),
        "The counters work because X adds 1 and O subtracts 1 on every line a cell belongs to; a line reaches &plusmn;N only when one player owns all N cells. That makes each move O(1) instead of O(N) or O(N&sup2;) for a rescan.",
    ],
    extend=[
        "A minimax player (perfect play on 3 &times; 3) is one more strategy. Undo is a stack of moves with the counter updates reversed. Networked play adds a <code>RemotePlayer</code> strategy whose <code>next_move</code> waits for a message.",
    ],
    questions=[
        question(
            "How does the O(1) win check work, and what if the win condition were K in a row on a large board (Gomoku)?",
            "medium",
            "With N in a row on an N &times; N board, each row, column and the two diagonals has a single counter. For K &lt; N in a row, counters per line do not work; instead, after a move at (r, c), walk outward in each of the four directions counting consecutive same marks: O(K) per move, still independent of board size.",
        ),
        question(
            "Where would you put input validation for a human player?",
            "medium",
            "In two places with different jobs: the human player strategy parses and re-prompts on malformed input (that is a UI concern), and <code>Board.place</code> rejects illegal moves regardless of who made them (that is a rule of the game). Never rely on the player object alone; a buggy AI or a malicious remote client must not be able to corrupt the board.",
        ),
    ],
)


SNAKES_LADDERS = problem(
    id="snakes-and-ladders",
    title="Design Snakes and Ladders",
    level="easy",
    patterns=["Strategy", "Builder"],
    summary="Board of jumps, players, pluggable dice, deterministic tests with seeded or scripted dice.",
    statement=[
        "Design a snakes-and-ladders game for any number of players on a 100-square board. The board layout is configurable, and the game must be testable without randomness getting in the way.",
    ],
    requirements=[
        "Players start at 0 and move by the die roll. Landing on a ladder's foot or a snake's head moves the player to the other end. A player needs an exact roll to land on 100 (an overshoot means no move). First to 100 wins.",
    ],
    choose=[
        ["Dice may be one die, two dice, or scripted for tests", "Strategy", "The game asks a <code>Dice</code> for a roll; tests inject fixed rolls"],
        ["Board layout configured from data and validated", "Builder", "Build the jump map step by step; validate no loops or conflicting starts"],
    ],
    classes=[
        ["<code>BoardBuilder</code>", "Adds snakes and ladders, validates, builds a <code>Board</code>"],
        ["<code>Board</code>", "Size and a jump map (start &rarr; end)"],
        ["<code>Dice</code>", "Strategy: <code>roll()</code>"],
        ["<code>Game</code>", "Players, turn order, <code>play()</code>"],
    ],
    implementation=[
        code('''
            import random
            from itertools import cycle

            class Board:
                def __init__(self, size, jumps):
                    self.size, self.jumps = size, jumps
                def move(self, pos, roll):
                    target = pos + roll
                    if target > self.size:
                        return pos, "overshoot"
                    if target in self.jumps:
                        end = self.jumps[target]
                        return end, ("ladder" if end > target else "snake") + f" {target}->{end}"
                    return target, ""

            class BoardBuilder:
                def __init__(self, size=100):
                    self.size, self.jumps = size, {}
                def _add(self, start, end):
                    if not (1 < start < self.size and 0 < end < self.size or end == self.size):
                        raise ValueError(f"jump {start}->{end} is off the board")
                    if start in self.jumps or start in self.jumps.values():
                        raise ValueError(f"square {start} already has a jump")
                    self.jumps[start] = end
                    return self
                def ladder(self, bottom, top):
                    if top <= bottom: raise ValueError("a ladder must go up")
                    return self._add(bottom, top)
                def snake(self, head, tail):
                    if tail >= head: raise ValueError("a snake must go down")
                    return self._add(head, tail)
                def build(self): return Board(self.size, dict(self.jumps))

            class RandomDie:
                def __init__(self, seed=None): self.rng = random.Random(seed)
                def roll(self): return self.rng.randint(1, 6)

            class Scripted:
                def __init__(self, rolls): self.rolls = iter(rolls)
                def roll(self): return next(self.rolls)

            class Game:
                def __init__(self, board, players, dice):
                    self.board, self.dice = board, dice
                    self.pos = {p: 0 for p in players}
                    self.order = cycle(players)
                def play(self, verbose=False, max_turns=10_000):
                    for turn in range(1, max_turns + 1):
                        p = next(self.order)
                        roll = self.dice.roll()
                        self.pos[p], event = self.board.move(self.pos[p], roll)
                        if verbose:
                            print(f"  {p} rolls {roll} -> {self.pos[p]:3} {event}")
                        if self.pos[p] == self.board.size:
                            return p, turn
                    raise RuntimeError("no winner")

            board = (BoardBuilder(30).ladder(3, 22).ladder(5, 8).snake(27, 1).snake(21, 9).build())
            print(Game(board, ["ann", "bob"], Scripted([3, 5, 5, 6, 4, 6, 6, 1, 6, 6, 6, 2, 5, 6, 4])).play(verbose=True))
            try:
                BoardBuilder(30).ladder(3, 22).snake(22, 4)
            except ValueError as e:
                print("ValueError:", e)
            wins = [Game(BoardBuilder().ladder(4, 56).snake(98, 2).build(), ["a", "b"], RandomDie(s)).play()[0]
                    for s in range(500)]
            print("first player wins", round(wins.count("a") / len(wins) * 100), "% of 500 seeded games")
        '''),
    ],
    extend=[
        "Rule variants (roll again on a six, three sixes sends you back) belong in a <code>Rules</code> strategy consulted by <code>Game</code>. Special squares (skip a turn) generalise the jump map into square effects &mdash; a small Command per square.",
    ],
    questions=[
        question(
            "How do you unit-test a game that depends on dice?",
            "medium",
            "Inject the dice. Tests pass a scripted die that returns a fixed sequence, so every scenario &mdash; a ladder chain, an overshoot near the end, a win on an exact roll &mdash; is reproducible. For statistical properties (no infinite games, plausible win distribution), use a seeded random die and run many games.",
        ),
        question(
            "What validation does the board builder need?",
            "medium",
            "Jumps must stay on the board; snakes go down and ladders up; a square cannot be the start of two jumps; a jump should not end on another jump's start (or decide the rule for chained jumps explicitly); the last square should not be a snake head. Doing this once in the builder means <code>Board</code> can assume a valid layout.",
        ),
    ],
)


CHESS = problem(
    id="chess",
    title="Design a Chess Game",
    level="hard",
    patterns=["Strategy", "Command", "Factory"],
    summary="Polymorphic pieces with move generation, move commands with undo, board set-up factory, check detection.",
    statement=[
        "Design the core of a chess engine for two players: a board, pieces with their movement rules, move validation (including not leaving your own king in check), and undo. Castling, en passant and promotion may be discussed as extensions.",
    ],
    requirements=[
        "Board 8 &times; 8; each piece type generates its pseudo-legal moves; a move is legal if it does not leave the mover's king in check; moves can be undone; the game reports check and checkmate.",
    ],
    choose=[
        ["Each piece moves differently", "Strategy / polymorphism", "One class per piece type with <code>moves(board, sq)</code>; sliding pieces share a helper"],
        ["Undo, move history, replay", "Command", "A <code>Move</code> records from, to and the captured piece, so it can be undone"],
        ["Standard starting position from a layout", "Factory", "Create pieces from FEN-like letters"],
    ],
    classes=[
        ["<code>Piece</code> and subclasses", "Colour; generate pseudo-legal target squares"],
        ["<code>Board</code>", "Square &rarr; piece map, apply/undo moves, find the king, attack test"],
        ["<code>Move</code>", "Command with <code>do</code> and <code>undo</code>"],
        ["<code>Game</code>", "Turn, legal move filter, history, status"],
    ],
    implementation=[
        code('''
            class Piece:
                symbol = "?"
                def __init__(self, white): self.white = white
                def __repr__(self): return self.symbol.upper() if self.white else self.symbol
                def slide(self, board, sq, dirs, max_steps=8):
                    r, c = sq
                    for dr, dc in dirs:
                        for k in range(1, max_steps + 1):
                            t = (r + dr * k, c + dc * k)
                            if not (0 <= t[0] < 8 and 0 <= t[1] < 8):
                                break
                            other = board.get(t)
                            if other is None:
                                yield t
                                continue
                            if other.white != self.white:
                                yield t                     # capture
                            break

            STRAIGHT = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            DIAGONAL = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

            class Rook(Piece):
                symbol = "r"
                def moves(self, b, sq): return self.slide(b, sq, STRAIGHT)
            class Bishop(Piece):
                symbol = "b"
                def moves(self, b, sq): return self.slide(b, sq, DIAGONAL)
            class Queen(Piece):
                symbol = "q"
                def moves(self, b, sq): return self.slide(b, sq, STRAIGHT + DIAGONAL)
            class King(Piece):
                symbol = "k"
                def moves(self, b, sq): return self.slide(b, sq, STRAIGHT + DIAGONAL, max_steps=1)
            class Knight(Piece):
                symbol = "n"
                def moves(self, b, sq):
                    for dr, dc in [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]:
                        t = (sq[0] + dr, sq[1] + dc)
                        if 0 <= t[0] < 8 and 0 <= t[1] < 8 and (b.get(t) is None or b.get(t).white != self.white):
                            yield t
            class Pawn(Piece):
                symbol = "p"
                def moves(self, b, sq):
                    d = 1 if self.white else -1
                    r, c = sq
                    if 0 <= r + d < 8 and b.get((r + d, c)) is None:
                        yield (r + d, c)
                        if r == (1 if self.white else 6) and b.get((r + 2 * d, c)) is None:
                            yield (r + 2 * d, c)
                    for dc in (-1, 1):
                        t = (r + d, c + dc)
                        if 0 <= t[1] < 8 and b.get(t) is not None and b.get(t).white != self.white:
                            yield t

            PIECES = {cls.symbol: cls for cls in (Rook, Bishop, Queen, King, Knight, Pawn)}

            def piece_from(letter):                      # factory
                return PIECES[letter.lower()](letter.isupper())

            class Move:                                  # command
                def __init__(self, frm, to): self.frm, self.to, self.captured = frm, to, None
                def do(self, board):
                    self.captured = board.pop(self.to, None)
                    board[self.to] = board.pop(self.frm)
                def undo(self, board):
                    board[self.frm] = board.pop(self.to)
                    if self.captured is not None:
                        board[self.to] = self.captured
                def __repr__(self):
                    f = lambda s: "abcdefgh"[s[1]] + str(s[0] + 1)
                    return f(self.frm) + f(self.to)

            class Game:
                def __init__(self, layout):
                    self.board = {}
                    for r, row in enumerate(layout):            # layout[0] is rank 1
                        for c, ch in enumerate(row):
                            if ch != ".":
                                self.board[(r, c)] = piece_from(ch)
                    self.white_to_move, self.history = True, []

                def attacked(self, sq, by_white):
                    return any(p.white == by_white and sq in set(p.moves(self.board, s))
                               for s, p in list(self.board.items()))

                def in_check(self, white):
                    king = next(s for s, p in self.board.items() if isinstance(p, King) and p.white == white)
                    return self.attacked(king, not white)

                def legal_moves(self):
                    out = []
                    for s, p in list(self.board.items()):
                        if p.white != self.white_to_move:
                            continue
                        for t in list(p.moves(self.board, s)):
                            m = Move(s, t); m.do(self.board)
                            if not self.in_check(self.white_to_move):
                                out.append(m)
                            m.undo(self.board)
                    return out

                def play(self, uci):
                    m = next((m for m in self.legal_moves() if repr(m) == uci), None)
                    if m is None:
                        raise ValueError(f"illegal move {uci}")
                    m.do(self.board); self.history.append(m)
                    self.white_to_move = not self.white_to_move

                def undo(self):
                    self.history.pop().undo(self.board)
                    self.white_to_move = not self.white_to_move

                def status(self):
                    moves = self.legal_moves()
                    check = self.in_check(self.white_to_move)
                    return "checkmate" if check and not moves else "stalemate" if not moves else "check" if check else "ok"

            START = ["RNBQKBNR", "PPPPPPPP", "........", "........",
                     "........", "........", "pppppppp", "rnbqkbnr"]
            g = Game(START)
            print("opening moves for white:", len(g.legal_moves()))
            for mv in ["f2f3", "e7e5", "g2g4", "d8h4"]:          # fool's mate
                g.play(mv)
            print("after fool's mate:", g.status(), "| history:", g.history)
            g.undo()
            print("after undo:", g.status(), "| black to move:", not g.white_to_move, "| legal:", len(g.legal_moves()))
            try:
                g.play("e8e6")
            except ValueError as e:
                print("ValueError:", e)
        '''),
        "Legality is checked by simulation: make each pseudo-legal move, ask whether the mover's king is attacked, undo. The Command object's undo is what makes that cheap and correct, and the same objects give the game its history.",
    ],
    extend=[
        "Castling, en passant and promotion are special <code>Move</code> subclasses with their own <code>do</code>/<code>undo</code> (castling moves two pieces, promotion replaces a pawn) plus a little extra state on the game (castling rights, en passant square). A computer opponent is a strategy that searches <code>legal_moves</code> with minimax.",
    ],
    questions=[
        question(
            "Why generate pseudo-legal moves per piece and then filter for check, instead of making each piece check legality?",
            "hard",
            "Whether a move leaves your king in check depends on the whole position (pins, discovered attacks), not on the moving piece's own rules. Keeping each piece responsible only for its movement pattern keeps piece classes simple and independent; one generic filter (do, test the king, undo) handles all the global rules uniformly. Fast engines optimise this with pin detection and attack maps, but the structure is the same.",
        ),
        question(
            "What does a <code>Move</code> need to store to support undo?",
            "medium",
            "The from and to squares, the captured piece (if any), and any game state the move changes that cannot be recomputed: castling rights, the en passant target square, the half-move clock for the fifty-move rule, and for promotion the original pawn. Storing these on the command keeps undo exact and O(1).",
        ),
    ],
)


CRICKET_SCOREBOARD = problem(
    id="cricket-scoreboard",
    title="Design a Live Cricket Scoreboard",
    level="medium",
    patterns=["Observer", "Command"],
    summary="Ball-by-ball events, derived score and stats, many live displays subscribed to updates, and correcting a wrong entry.",
    statement=[
        "Design the scoring core of a Cricbuzz-style app. A scorer records each delivery; the score, batting stats and commentary feeds update live for many viewers. Scorers sometimes enter a ball wrongly and need to undo it.",
    ],
    requirements=[
        "Record deliveries: runs, extras (wide, no-ball) and wickets. Derive total, wickets, overs (legal balls only), run rate and batter stats. Push updates to subscribers (scorecard widget, commentary, push notifications for wickets and milestones). Support undoing the last ball.",
    ],
    choose=[
        ["Many displays update when a ball is recorded", "Observer", "Displays subscribe; the scorer does not know them"],
        ["Each delivery is an event that can be undone", "Command / event sourcing", "Store balls, derive the score; undo = drop the last event and rebuild or reverse"],
    ],
    classes=[
        ["<code>Ball</code>", "Immutable event: batter, runs, extra, wicket"],
        ["<code>Innings</code>", "Event list, derived totals; <code>record</code>, <code>undo</code>"],
        ["Subscribers", "Scorecard, milestone alerts &mdash; callables receiving the innings after each change"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class Ball:
                batter: str
                runs: int = 0
                extra: str | None = None          # "wide" | "noball" | None
                wicket: bool = False

                @property
                def legal(self): return self.extra is None

            class Innings:
                def __init__(self):
                    self.balls, self.subscribers = [], []

                def subscribe(self, fn): self.subscribers.append(fn)

                def record(self, ball):
                    self.balls.append(ball)
                    self._notify(ball)

                def undo(self):
                    ball = self.balls.pop()
                    self._notify(None)
                    return ball

                def _notify(self, ball):
                    for fn in self.subscribers:
                        fn(self, ball)

                @property
                def total(self):
                    return sum(b.runs + (1 if b.extra else 0) for b in self.balls)

                @property
                def wickets(self): return sum(b.wicket for b in self.balls)

                @property
                def overs(self):
                    legal = sum(b.legal for b in self.balls)
                    return f"{legal // 6}.{legal % 6}"

                def batter_runs(self, name):
                    return sum(b.runs for b in self.balls if b.batter == name and b.extra != "wide")

            def scorecard(inn, ball):
                print(f"  {inn.total}/{inn.wickets} ({inn.overs} ov)")

            def milestones(inn, ball):
                if ball and ball.wicket:
                    print(f"  ALERT: wicket! {ball.batter} out for {inn.batter_runs(ball.batter)}")
                if ball and inn.batter_runs(ball.batter) >= 10 > inn.batter_runs(ball.batter) - ball.runs:
                    print(f"  ALERT: {ball.batter} reaches 10")

            inn = Innings()
            inn.subscribe(scorecard)
            inn.subscribe(milestones)
            for b in [Ball("rohit", 4), Ball("rohit", 1), Ball("gill", 0, "wide"), Ball("gill", 6),
                      Ball("gill", 4), Ball("gill", 0, wicket=True), Ball("kohli", 2)]:
                inn.record(b)
            print("scorer fixes a mistake:")
            inn.undo()
            print("rohit", inn.batter_runs("rohit"), "| gill", inn.batter_runs("gill"))
        '''),
        "Every number on the scorecard is derived from the list of balls, so undo is just removing the last ball and nothing can drift out of sync. Large systems keep this shape and add cached aggregates for speed, recomputed (or reversed) per event.",
    ],
    extend=[
        "Viewers on phones get updates through a pub/sub fan-out (the in-process observers above become a message broker topic per match). Commentary and analytics (wagon wheel, partnerships) are more subscribers. Undo of a ball broadcasts a correction event so clients can fix their state.",
    ],
    questions=[
        question(
            "Should the scoreboard store the current score or the ball-by-ball events?",
            "medium",
            "Store events and derive the score (event sourcing). It makes corrections trivial and auditable, lets you add new statistics later by replaying history, and guarantees all views agree. For performance, also maintain running totals updated per event, treating them as a cache that can be rebuilt from the events.",
        ),
        question(
            "Ten million people follow a match. How do updates reach them?",
            "hard",
            "The scoring service publishes each ball event to a topic for that match. Edge servers holding WebSocket or SSE connections subscribe to the topic and push to their connected clients; each server serves tens of thousands of clients, so the fan-out is a tree. Clients that miss updates (reconnect, background) fetch the current state snapshot with a sequence number and then apply further events. Push notifications for wickets go through APNs/FCM in batches.",
        ),
    ],
)


AUCTION = problem(
    id="online-auction",
    title="Design an Online Auction System",
    level="medium",
    patterns=["State", "Observer", "Strategy"],
    summary="Auction lifecycle states, bid validation with increments, outbid notifications, pluggable winner rules.",
    statement=[
        "Design an eBay-style auction. Sellers list an item with a starting price and end time; buyers place bids; bidders are notified when they are outbid; when the auction ends, the winner is determined and notified.",
    ],
    requirements=[
        "Lifecycle: draft &rarr; live &rarr; ended (or cancelled). Bids are accepted only while live, must exceed the current highest bid by a minimum increment, and must not come from the seller. Notify the previous leader when outbid. Winner rule: highest bid (English auction), with a reserve price; a second-price rule should be possible.",
    ],
    choose=[
        ["Bids allowed only while the auction is live", "State", "Each lifecycle state accepts or rejects actions"],
        ["&ldquo;Notify bidders when outbid&rdquo; and the winner at the end", "Observer", "Notification channels subscribe to auction events"],
        ["Highest bid wins vs second-price (Vickrey)", "Strategy", "The settlement rule is pluggable"],
    ],
    classes=[
        ["<code>Auction</code>", "Item, seller, state, bids, listeners"],
        ["<code>Bid</code>", "Bidder, amount, time"],
        ["<code>SettlementRule</code>", "Strategy: winner and price from the bids"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class Bid:
                bidder: str
                amount: int
                t: int

            class HighestBid:
                def settle(self, bids, reserve):
                    top = max(bids, key=lambda b: (b.amount, -b.t), default=None)
                    return (top.bidder, top.amount) if top and top.amount >= reserve else (None, 0)

            class SecondPrice:
                def settle(self, bids, reserve):
                    ranked = sorted(bids, key=lambda b: (-b.amount, b.t))
                    if not ranked or ranked[0].amount < reserve:
                        return None, 0
                    second = ranked[1].amount if len(ranked) > 1 else reserve
                    return ranked[0].bidder, max(second, reserve)

            class Auction:
                def __init__(self, item, seller, start, reserve, increment, rule):
                    self.item, self.seller, self.reserve, self.increment = item, seller, reserve, increment
                    self.start, self.rule = start, rule
                    self.state, self.bids, self.listeners = "draft", [], []

                def emit(self, event, **kw):
                    for fn in self.listeners: fn(event, kw)

                def open(self):
                    if self.state != "draft": raise RuntimeError(f"cannot open a {self.state} auction")
                    self.state = "live"

                def bid(self, bidder, amount, t):
                    if self.state != "live":
                        raise RuntimeError(f"auction is {self.state}")
                    if bidder == self.seller:
                        raise PermissionError("seller cannot bid")
                    leader = self.bids[-1] if self.bids else None
                    minimum = leader.amount + self.increment if leader else self.start
                    if amount < minimum:
                        raise ValueError(f"bid must be at least {minimum}")
                    self.bids.append(Bid(bidder, amount, t))
                    if leader and leader.bidder != bidder:
                        self.emit("outbid", who=leader.bidder, by=amount)

                def close(self):
                    if self.state != "live": raise RuntimeError(f"cannot close a {self.state} auction")
                    self.state = "ended"
                    winner, price = self.rule.settle(self.bids, self.reserve)
                    self.emit("ended", winner=winner, price=price)
                    return winner, price

            def run(rule):
                a = Auction("guitar", "sam", start=100, reserve=150, increment=10, rule=rule)
                a.listeners.append(lambda e, d: print(f"  {e}: {d}"))
                a.open()
                for who, amt, t in [("ann", 100, 1), ("bob", 120, 2), ("ann", 125, 3), ("ann", 140, 4), ("cy", 200, 5)]:
                    try:
                        a.bid(who, amt, t)
                    except ValueError as e:
                        print(f"  {who} {amt}: {e}")
                return a.close()

            print("English:", run(HighestBid()))
            print("Second-price:", run(SecondPrice()))
            a = Auction("vase", "sam", 50, 0, 5, HighestBid())
            try:
                a.bid("ann", 60, 1)
            except RuntimeError as e:
                print("RuntimeError:", e)
        '''),
    ],
    extend=[
        "Auto-bidding (proxy bids: &ldquo;bid for me up to 300&rdquo;) is a component that listens for outbid events on behalf of a user and places the next increment. Anti-sniping extends the end time when a bid arrives in the last minute &mdash; a rule inside the live state. Closing at the end time is a scheduled job; it must be idempotent in case it fires twice.",
    ],
    questions=[
        question(
            "Two bids arrive in the same millisecond for the last increment. How do you keep bidding consistent?",
            "hard",
            "Serialise bids per auction: process them through a single-threaded actor or a queue partitioned by auction id, or do a conditional write in the database (<code>UPDATE auctions SET top_bid=?, leader=? WHERE id=? AND top_bid=?</code>, retrying on failure). Either way, the &ldquo;must exceed the current leader&rdquo; check and the update happen atomically, and ties are broken by arrival order at that serialisation point.",
        ),
        question(
            "Why is the settlement rule a strategy and not part of the auction?",
            "medium",
            "It is the part most likely to vary by marketplace or listing type (English, second-price, Dutch, reserve or not), and it is a pure function of the bids and the reserve, which makes it easy to test in isolation. The auction keeps the lifecycle and bid validation, which are shared by every rule.",
        ),
    ],
)

PROBLEMS = [TIC_TAC_TOE, SNAKES_LADDERS, CHESS, CRICKET_SCOREBOARD, AUCTION]
