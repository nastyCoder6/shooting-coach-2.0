import numpy as np

class GeometryEngine:
    """ Silnik matematyczny systemu. Odpowiada za obliczenia wektorowe i wyznaczanie kątów w przestrzeni auklidesowej. """

    @staticmethod
    def calculate_angle3d(p1, p2, p3) -> float:
        """
        Oblicza kąt (w stopniach) w punkcie p2, utworzony przez punkty p1 i p3.
        Wykorzystuje przekształcone twierdzenie cosinusów.
        """

        # konwersja punktów na wektory
        a = np.array([p1.x, p1.y, p1.z])
        b = np.array([p2.x, p2.y, p2.z])
        c = np.array([p3.x, p3.y, p3.z])

        # tworzenie wektorów u i v
        u = a-b
        v = c-b

        # obliczenie cosinusu kąta
        cosine_angle = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        
        # klipowanie wartości celem uniknięcia błędów numerycznych arccos
        cosine_angle = np.clip(cosine_angle, -1, 1)

        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    @staticmethod
    def calculate_velocity(p_t0, p_t1, time_delta: float) -> float:
        """
        Oblicza prędkość przemieszczenia punktu między klatkami. Potrzebne do wykrywania momentu 'release point'.
        """
        if time_delta <= 0:
            return 0.0
        
        p0 = np.array([p_t0.x, p_t0.y])
        p1 = np.array([p_t1.x, p_t1.y])
        
        dist = np.linalg.norm(p1 - p0)
        return dist / time_delta