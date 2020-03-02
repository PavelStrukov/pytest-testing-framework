

def get_list_of_students(list_of_dicts):
    """Parses the list of students

    Parameters
    ----------
    list_of_dicts : list
        List of students as dictionaries

    Returns
    -------
    list
        A list of Student objects"""

    students = []
    for student in list_of_dicts:
        created_student = Student(student_as_dict=student)
        students.append(created_student)
    return students


class Student:
    """
    Class Student represents the model of the students
    ...

    Attributes
    ----------
    id : int
        Student's id
    name : str
        The name of the student
    login : str
        The login of the student
    password : string
        The password of the student
    group_id : int
        The id of the group where the student studies
    """

    def __init__(self, student_as_dict=None, id=None, name=None, login=None, password=None, group_id=None):

        """Parameters
        ----------
        student_as_dict: dictionary, , optional (default is None)
            If we want to create student object from dictionary
        id : int, optional (default is None)
            Student's id
        name : str, optional (default is None)
            The name of the student
        login : str, optional (default is None)
            The login of the student
        password : string, optional (default is None)
            The password of the student
        group_id : int, optional (default is None)
            The id of the group where the student studies

        Raises
        ------
        ValueError
            If the types of parameters are illegal or wrong number of params"""

        # If we create student from existing dictionary
        if student_as_dict is not None:
            for key, value in student_as_dict.items():
                if key == "name" or key == "login" or key == "password":
                    value = "'" + value + "'"
                setattr(self, key, value)
        else:
            self.id = id
            self.name = "'" + name + "'"
            self.login = "'" + login + "'"
            self.password = "'" + password + "'"
            self.group_id = group_id

    def __eq__(self, other):

        """Override the default Equals behavior.
        Compares by equality of all parameters"""

        if isinstance(other, self.__class__):
            return self.id == other.id and self.name == other.name and \
                   self.login == other.login and self.password == other.password and \
                   self.group_id == other.group_id
        return False
