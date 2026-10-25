from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    kind: str           # "start" | "evaluate" | "accept"
    move: str | None    # "swap1" | "swap2" | None (для start)
    parent: tuple | None
    child: tuple
    value: float


@dataclass
class Tracer:
    """
    Записывает ход поиска: каждое вычисленное соседнее решение и каждый принятый переход.
    """
    events: list[Event] = field(default_factory=list)

    def start(self, y, value):
        self.events.append(Event("start", None, None, tuple(y), value))

    def evaluate(self, parent, child, value, move):
        self.events.append(Event("evaluate", move, tuple(parent), tuple(child), value))

    def accept(self, parent, child, value, move):
        self.events.append(Event("accept", move, tuple(parent), tuple(child), value))
