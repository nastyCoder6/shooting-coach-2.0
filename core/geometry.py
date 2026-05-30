import numpy as np

class GeometryEngine:
    """
    Silnik geometryczny zoptymalizowany pod analizę wideo 2D.
    Eliminuje błędy predykcji głębi (z-jitter) z biblioteki MediaPipe.
    """
    
    def _to_numpy_2d(self, p):
        """
        Prywatna metoda pomocnicza.
        Pobiera wyłącznie koordynaty X oraz Y, ignorując niestabilną oś Z.
        """
        if isinstance(p, dict):
            return np.array([p.get('x', 0.0), p.get('y', 0.0)])
        elif hasattr(p, 'x'):
            return np.array([p.x, p.y])
        return np.array(p[:2])

    def calculate_angle2d(self, p1, p2, p3) -> float:
        """
        Oblicza kąt 2D (w stopniach) rzutowany na płaszczyznę ekranu kamery.
        Daje stabilne, zgodne z ludzkim okiem wyniki.
        """
        a = self._to_numpy_2d(p1)
        b = self._to_numpy_2d(p2)
        c = self._to_numpy_2d(p3)

        ba = a - b
        bc = c - b

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba == 0.0 or norm_bc == 0.0:
            return 0.0

        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        
        angle = np.degrees(np.arccos(cosine_angle))
        
        return float(angle)

    def calculate_velocity(self, p_prev, p_curr, time_delta: float) -> float:
        """
        Oblicza prędkość punktu w przestrzeni 2D ekranu.
        """
        if time_delta <= 0:
            return 0.0
            
        prev = self._to_numpy_2d(p_prev)
        curr = self._to_numpy_2d(p_curr)
        
        distance = np.linalg.norm(curr - prev)
        velocity = distance / time_delta
        return float(velocity)