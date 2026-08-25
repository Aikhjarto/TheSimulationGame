import math
from collections import deque
from dataclasses import dataclass


@dataclass
class Cell:
    def __init__(
        self,
        vegetation: float = 20.0,
        grazer: float = 8.0,
        predator: float = 3.0,
        k_v: float = 0.50,
        k_g: float = 0.15,
        k_gv: float = 1/3.0,
        k_gp: float = 0.01,
        k_p: float = 0.2,
        k_pg: float = 1/2.0,
        max_vegetation: float = 100.0,
        max_grazer: float = 50.0,
        max_predator: float = 30.0,
        hist_length: int = 1000,
        activation_mode: str = "tanh",
        name: str = "cell",
    ):
        self.vegetation: float = vegetation
        self.grazer: float = grazer
        self.predator: float = predator
        self.name: str = name

        self.grazer_transfer: float = 0.0
        self.predator_transfer: float = 0.0

        self.k_v: float = k_v
        self.k_g: float = k_g
        self.k_gv: float = k_gv
        self.k_gp: float = k_gp
        self.k_p: float = k_p
        self.k_pg: float = k_pg

        self.max_vegetation: float = max_vegetation
        self.max_grazer: float = max_grazer
        self.max_predator: float = max_predator

        self.activation_mode: str = activation_mode  # tanh or 'logarithmic'

        self._hist_length = 1000
        self.hist_vegetation: deque[float] = deque(maxlen=self._hist_length)
        self.hist_grazer: deque[float] = deque(maxlen=self._hist_length)
        self.hist_predator: deque[float] = deque(maxlen=self._hist_length)
        self.hist_length = (
            hist_length  # Initialize history deques with the specified length
        )

        self._starved_grazers: float | None= None
        self._starved_predators: float | None= None

    @property
    def starved_grazers(self) -> float:
        """Return the number of grazers that are starved (i.e., not enough vegetation)."""
        self._starved_grazers = (
            self.k_g
            * self.grazer
            * self._act(self.activation_mode, self.k_gv * self.vegetation, self.grazer)
        )
        return max(0.0, self._starved_grazers)  # Ensure non-negative value

    @property
    def starved_predators(self) -> float:
        """Return the number of predators that are starved (i.e., not enough grazers)."""
        self._starved_predators = (
            self.k_p
            * self.predator
            * self._act(self.activation_mode, self.k_pg * self.grazer, self.predator)
        )
        return max(0.0, self._starved_predators)  # Ensure non-negative value

    @staticmethod
    def _act(activation_mode: str, a: float, b: float) -> float:
        """
        If a > b, return value is positive, if a < b, return value is negative.
        """
        if activation_mode == "logarithmic":
            if b < 0.0 or a < 0.0:
                raise RuntimeError(
                    f"Logarithm of non-positive value encountered"
                    f"for numerator={a}, denominator={b}"
                )
            elif b > 0.0 and a == 0.0:
                return -float("inf")
            elif b == 0.0 and a > 0.0:
                return float("inf")
            elif a == 0.0 and b == 0.0:
                return 1.0
            else:
                return math.log(a / b)
        elif activation_mode == "tanh":
            return math.tanh(a - b)
        else:
            raise NotImplementedError(f"Unknown activation mode: {activation_mode}")

    def tick(self):

        # apply transfer of grazers and predators from neighboring cells
        self.grazer += self.grazer_transfer
        self.predator += self.predator_transfer

        vegetation_derivative = (
            self.k_v * self.vegetation * (1.0 - self.vegetation / self.max_vegetation)
            - self.k_g * self.grazer
        )
        grazer_derivative = (
            self.k_g
            * self.grazer
            * self._act(self.activation_mode, self.k_gv * self.vegetation, self.grazer)
            - self.k_gp * self.predator
        )
        predator_derivative = (
            self.k_p
            * self.predator
            * self._act(self.activation_mode, self.k_pg * self.grazer, self.predator)
        )

        self.vegetation = self.vegetation + vegetation_derivative
        self.grazer = self.grazer + grazer_derivative
        self.predator = self.predator + predator_derivative
        self.clamp_non_negative()
        self.append_hist()

    def clamp_non_negative(self) -> None:
        self.vegetation = max(0.0, self.vegetation)
        self.grazer = max(0.0, self.grazer)
        self.predator = max(0.0, self.predator)

    def append_hist(self):
        self.hist_vegetation.append(self.vegetation)
        self.hist_grazer.append(self.grazer)
        self.hist_predator.append(self.predator)

    @property
    def hist_length(self) -> int:
        return self._hist_length

    @hist_length.setter
    def hist_length(self, len: int):
        self.hist_vegetation = deque(self.hist_vegetation, maxlen=len)
        self.hist_grazer = deque(self.hist_grazer, maxlen=len)
        self.hist_predator = deque(self.hist_predator, maxlen=len)
