"""Reporting helper for the variant 1 student registry."""
from student_testing.registry import InMemoryStudentRepository, best_student, group_average, make_student


def main() -> None:
    students = [
        make_student(1, "Марія", "Дорош", "ФЕП-32", 86.5),
        make_student(2, "Данило", "Левицький", "ФЕП-31", 95.0),
        make_student(3, "Соломія", "Климчук", "ФЕП-32", 91.5),
        make_student(4, "Остап", "Мазур", "ФЕП-31", 78.0),
        make_student(5, "Олена", "Романюк", "ФЕП-33", 85.0),
        make_student(6, "Тарас", "Дорош", "ФЕП-33", 72.0),
    ]
    repo = InMemoryStudentRepository(students)
    selected = repo.list_all()
    for student in selected:
        print(f"{student.student_id:<3} {student.first_name:<10} {student.last_name:<13} {student.group:<8} {student.average_grade:.1f}")
    print(f"Середній бал ФЕП-32: {group_average(selected, 'ФЕП-32'):.2f}")
    winner = best_student(selected)
    if winner:
        print(f"Найкращий студент: {winner.first_name} {winner.last_name} ({winner.average_grade:.1f})")


if __name__ == "__main__":
    main()
