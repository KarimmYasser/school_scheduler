"""
Solver Factory - Central management of all scheduling algorithms

This module provides a unified interface to all scheduling solvers,
making it easy to add new algorithms and switch between them.
"""

import time
from typing import Dict, Any, Optional
from enum import Enum

class SolverType(Enum):
    """Available solver types"""
    ULTRA_FAST = "ultra_fast"
    SMART_GREEDY = "smart_greedy"
    ML_INSPIRED = "ml_inspired" 
    FAST_GREEDY = "fast_greedy"
    ORTOOLS = "ortools"
    SIMPLE = "simple"

class SolverResult:
    """Result of a scheduling operation"""
    def __init__(self, success: bool, lessons_count: int, 
                 time_taken: float, algorithm: str, error: str = None):
        self.success = success
        self.lessons_count = lessons_count
        self.time_taken = time_taken
        self.algorithm = algorithm
        self.error = error

class SolverFactory:
    """Factory class for creating and managing solvers"""
    
    @staticmethod
    def get_solver_info() -> Dict[str, Dict[str, Any]]:
        """Get information about all available solvers"""
        return {
            SolverType.ULTRA_FAST.value: {
                "name": "⚡ Ultra-Fast (Recommended)",
                "description": "Optimized ultra-fast algorithm\n• Typical time: < 0.5 seconds\n• Quality: Very Good\n• Best for: Instant scheduling",
                "typical_time": "< 0.5s",
                "quality": "Very Good",
                "best_for": "Instant scheduling"
            },
            SolverType.SMART_GREEDY.value: {
                "name": "🚀 Smart Greedy", 
                "description": "Intelligent greedy with heuristics\n• Typical time: < 1 second\n• Quality: Excellent\n• Best for: Fast + high quality",
                "typical_time": "< 1s",
                "quality": "Excellent", 
                "best_for": "Fast + high quality"
            },
            SolverType.ML_INSPIRED.value: {
                "name": "🧠 ML-Inspired Scheduler",
                "description": "Pattern-learning algorithm\n• Typical time: 1-3 seconds\n• Quality: Excellent\n• Best for: Learning from data",
                "typical_time": "1-3s",
                "quality": "Excellent",
                "best_for": "Learning from data"
            },
            SolverType.FAST_GREEDY.value: {
                "name": "🎯 Fast Greedy",
                "description": "Basic fast greedy algorithm\n• Typical time: < 1 second\n• Quality: Good\n• Best for: Quick results", 
                "typical_time": "< 1s",
                "quality": "Good",
                "best_for": "Quick results"
            },
            SolverType.ORTOOLS.value: {
                "name": "🔧 OR-Tools (Classic)",
                "description": "Google's constraint solver\n• Typical time: 10-30 seconds\n• Quality: Optimal\n• Best for: Guaranteed optimality",
                "typical_time": "10-30s", 
                "quality": "Optimal",
                "best_for": "Guaranteed optimality"
            },
            SolverType.SIMPLE.value: {
                "name": "🔄 Simple Fallback",
                "description": "Basic fallback algorithm\n• Typical time: < 2 seconds\n• Quality: Good\n• Best for: Compatibility",
                "typical_time": "< 2s",
                "quality": "Good", 
                "best_for": "Compatibility"
            }
        }
    
    @staticmethod
    def solve(solver_type: SolverType, db_file: str = "data/database/school_timetable.db") -> SolverResult:
        """
        Solve scheduling using the specified algorithm
        
        Args:
            solver_type: Type of solver to use
            db_file: Path to database file
            
        Returns:
            SolverResult with success status and metrics
        """
        start_time = time.time()
        
        try:
            if solver_type == SolverType.ULTRA_FAST:
                from .ultra_fast_solver import solve_ultra_fast
                success = solve_ultra_fast("ultra_fast", db_file)
                
            elif solver_type == SolverType.SMART_GREEDY:
                from .ultra_fast_solver import solve_ultra_fast
                success = solve_ultra_fast("smart_greedy", db_file)
                
            elif solver_type == SolverType.ML_INSPIRED:
                from .ml_solver import solve_with_ml_scheduler
                success = solve_with_ml_scheduler(db_file)
                
            elif solver_type == SolverType.FAST_GREEDY:
                from .fast_solver import solve_with_fast_scheduler
                success = solve_with_fast_scheduler("greedy", db_file)
                
            elif solver_type == SolverType.ORTOOLS:
                try:
                    from .ortools_solver import solve_school_scheduling_from_db
                    solution = solve_school_scheduling_from_db(db_file)
                    success = solution is not None
                except ImportError:
                    return SolverResult(False, 0, 0, solver_type.value, 
                                      "OR-Tools not available. Please install: pip install ortools")
                    
            elif solver_type == SolverType.SIMPLE:
                from .greedy_solver import solve_school_scheduling_from_db
                solution = solve_school_scheduling_from_db(db_file)
                success = solution is not None
                
            else:
                return SolverResult(False, 0, 0, solver_type.value, f"Unknown solver type: {solver_type}")
            
            end_time = time.time()
            time_taken = end_time - start_time
            
            # Count generated lessons
            lessons_count = 0
            if success:
                import sqlite3
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM schedules WHERE is_locked = 0")
                lessons_count = cursor.fetchone()[0]
                conn.close()
            
            return SolverResult(success, lessons_count, time_taken, solver_type.value)
            
        except Exception as e:
            end_time = time.time()
            time_taken = end_time - start_time
            return SolverResult(False, 0, time_taken, solver_type.value, str(e))
    
    @staticmethod
    def get_recommended_solver(num_classes: int = 20, num_teachers: int = 50) -> SolverType:
        """
        Get recommended solver based on dataset size
        
        Args:
            num_classes: Number of classes
            num_teachers: Number of teachers
            
        Returns:
            Recommended solver type
        """
        total_entities = num_classes + num_teachers
        
        if total_entities < 30:
            return SolverType.ULTRA_FAST
        elif total_entities < 100:
            return SolverType.SMART_GREEDY
        elif total_entities < 200:
            return SolverType.ML_INSPIRED
        else:
            return SolverType.FAST_GREEDY