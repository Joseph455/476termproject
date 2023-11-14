from typing import Any


class Course:
    """Class representing cource phenotype."""
    __class_id: int = 1
    id: int
    code: str
    required_periods: int
    students_population: int

    def __init__(self, code: str, students_population: int, required_periods: int = 1):
        self.id = Course.__class_id
        Course.__class_id += 1
        self.code = code
        self.required_periods = required_periods
        self.students_population = students_population
    
    def __str__(self) -> str:
        return f'<Cource id={self.id}, code={self.code}, required_periods={self.required_periods}, population={self.students_population}>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert cource to dict format."""
        return {
            'code': self.code,
            'required_periods': self.required_periods,
            'students_population': self.students_population,
        }


class Day:
    """Class representing day phenotype."""
    __class_id: int = 1
    id: int
    date: str
    periods: list[int] 

    def __init__(self, date: str, periods: list[int]) -> None:
        self.id = Day.__class_id
        Day.__class_id += 1
        self.date = date
        self.periods = periods
    
    def __str__(self) -> str:
        return f'<Day id={self.id},  periods={self.periods}, date={self.date}>'

    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert day to dict format."""
        return {
            'date': self.date,
            'periods': self.periods,
        }


class Venue:
    """Class representing a venue phenotype."""
    __class_id: int = 1
    id: int
    title: str
    capacity: int

    def __init__(self, title: str, capacity: int) -> None:
        self.id = Venue.__class_id
        Venue.__class_id += 1
        self.title = title
        self.capacity = capacity

    def __str__(self) -> str:
        return f'<Venue id={self.id} title={self.title}, capacity={self.capacity}>'

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict[str, Any]:
        """Convert venue to dict format."""
        return {
            'date': self.title,
            'periods': self.capacity,
        }
