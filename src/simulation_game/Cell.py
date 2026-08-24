import math
from collections import deque
from dataclasses import dataclass


@dataclass
class Cell:
    def __init__(
        self,
        plant: float = 20.0,
        grazer: float = 8.0,
        predator: float = 3.0,
        k_v: float = 0.10,
        k_g: float = 0.15,
        k_gv: float = 1.0,
        k_gp: float = 0.01,
        k_p: float = 0.2,
        k_pg: float = 1.0,
        max_plant: float = 100.0,
        max_grazer: float = 50.0,
        max_predator: float = 30.0,
        hist_length: int = 1000,
        activation_mode: str = "tanh",
        name: str = "cell",
    ):
        self.plant: float = plant
        self.grazer: float = grazer
        self.predator: float = predator
        self.name: str = name

        self.k_v: float = k_v
        self.k_g: float = k_g
        self.k_gv: float = k_gv
        self.k_gp: float = k_gp
        self.k_p: float = k_p
        self.k_pg: float = k_pg

        self.max_plant: float = max_plant
        self.max_grazer: float = max_grazer
        self.max_predator: float = max_predator

        self.activation_mode: str = activation_mode  # tanh or 'logarithmic'

        self._hist_length = 1000
        self.hist_plant: deque[float] = deque(maxlen=self._hist_length)
        self.hist_grazer: deque[float] = deque(maxlen=self._hist_length)
        self.hist_predator: deque[float] = deque(maxlen=self._hist_length)
        self.hist_length = (
            hist_length  # Initialize history deques with the specified length
        )

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
        vegetation = self.plant
        grazers = self.grazer
        predators = self.predator
        vegetation_derivative = (
            self.k_v * vegetation * (1.0 - vegetation / self.max_plant)
            - self.k_g * grazers
        )
        grazer_derivative = (
            self.k_g
            * grazers
            * self._act(self.activation_mode, self.k_gv * vegetation, grazers)
            - self.k_gp * predators
        )
        predator_derivative = (
            self.k_p
            * predators
            * self._act(self.activation_mode, self.k_pg * grazers, predators)
        )

        self.plant = vegetation + vegetation_derivative
        self.grazer = grazers + grazer_derivative
        self.predator = predators + predator_derivative
        self.clamp_non_negative()
        self.append_hist()

    def clamp_non_negative(self) -> None:
        self.plant = max(0.0, self.plant)
        self.grazer = max(0.0, self.grazer)
        self.predator = max(0.0, self.predator)

    def append_hist(self):
        self.hist_plant.append(self.plant)
        self.hist_grazer.append(self.grazer)
        self.hist_predator.append(self.predator)

    @property
    def hist_length(self) -> int:
        return self._hist_length

    @hist_length.setter
    def hist_length(self, len: int):
        self.hist_plant = deque(self.hist_plant, maxlen=len)
        self.hist_grazer = deque(self.hist_grazer, maxlen=len)
        self.hist_predator = deque(self.hist_predator, maxlen=len)
