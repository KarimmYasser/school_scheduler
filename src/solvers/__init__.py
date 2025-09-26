"""Scheduling Solvers Package"""

from .solver_factory import SolverFactory, SolverType, SolverResult

# Import individual solvers for direct access if needed
from .fast_solver import solve_with_fast_scheduler
from .greedy_solver import solve_school_scheduling_from_db
from .ml_solver import solve_with_ml_scheduler
from .ultra_fast_solver import solve_ultra_fast

try:
    from .ortools_solver import solve_school_scheduling_from_db as solve_with_ortools
except ImportError:
    solve_with_ortools = None

__all__ = [
    'SolverFactory',
    'SolverType', 
    'SolverResult',
    'solve_with_fast_scheduler',
    'solve_school_scheduling_from_db', 
    'solve_with_ml_scheduler',
    'solve_ultra_fast',
    'solve_with_ortools'
]