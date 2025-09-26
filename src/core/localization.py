"""
Localization system for the School Timetable Generator
Supports English and Arabic languages with right-to-left text support
"""

import json
import os
from typing import Dict, Optional

class Localization:
    """Handles application localization and language switching"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize localization system
        
        Args:
            language: Language code ('en' for English, 'ar' for Arabic)
        """
        self.current_language = language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files"""
        # Define translations directly in code for now
        self.translations = {
            "en": {
                # Main Window
                "app_title": "School Timetable Generator",
                "view_label": "View:",
                "classes": "Classes",
                "teachers": "Teachers",
                "generate_schedule": "Generate Schedule",
                
                # Menu Items - Data
                "menu_data": "Data",
                "manage_teachers": "Manage Teachers",
                "manage_classes": "Manage Classes", 
                "manage_subjects": "Manage Subjects",
                "manage_rooms": "Manage Rooms",
                "set_lesson_requirements": "Set Lesson Requirements",
                "teacher_preferences": "Teacher Preferences",
                "teacher_availability": "Teacher Availability",
                
                # Menu Items - Tools
                "menu_tools": "Tools",
                "menu_rules": "Rules",
                "scheduling_rules": "Scheduling Rules",
                "constraint_settings": "Constraint Settings",
                "time_settings": "Time Settings",
                "database_statistics": "Database Statistics",
                "clear_all_schedules": "Clear All Schedules",
                "import_sample_data": "Import Sample Data",
                "backup_database": "Backup Database",
                
                # Menu Items - Language
                "menu_language": "Language",
                "english": "English",
                "arabic": "العربية",
                
                # Days of week
                "monday": "Monday",
                "tuesday": "Tuesday", 
                "wednesday": "Wednesday",
                "thursday": "Thursday",
                "friday": "Friday",
                "saturday": "Saturday",
                "sunday": "Sunday",
                
                # Time periods
                "period": "Period",
                "time_slot": "Time Slot",
                "free": "Free",
                
                # Timetable editing
                "edit": "Edit",
                "editing": "Editing",
                "time": "Time",
                "current_assignment": "Current Assignment:",
                "subject": "Subject",
                "teacher": "Teacher",
                "class": "Class", 
                "room": "Room",
                "remove_lesson": "Remove Lesson",
                "move_lesson": "Move Lesson",
                "move_lesson_title": "Move Lesson",
                "select_new_time_slot": "Select new time slot:",
                "select": "Select",
                "current": "Current",
                "close": "Close",
                
                # Data management
                "manage": "Manage",
                "id": "ID",
                "name": "Name",
                "add": "Add",
                "edit": "Edit", 
                "delete": "Delete",
                "refresh": "Refresh",
                
                # Success/Error Messages
                "success": "Success",
                "lesson_requirements_generated": "Lesson requirements generated successfully!",
                "all_schedules_cleared": "All schedules cleared!",
                "sample_data_imported": "Sample data imported!",
                "backup_created": "Backup Created",  
                "backup_failed": "Backup Failed",
                "database_backed_up": "Database backed up as",
                "failed_to_create_backup": "Failed to create backup",
                
                # Algorithm Selection Dialog
                "select_algorithm": "Select Scheduling Algorithm",
                "choose_algorithm": "Choose Scheduling Algorithm",
                "generate": "🚀 Generate Schedule",
                "cancel": "❌ Cancel",
                
                # Algorithm Names
                "ultra_fast": "⚡ Ultra-Fast (Recommended)",
                "smart_greedy": "🚀 Smart Greedy",
                "ml_inspired": "🧠 ML-Inspired Scheduler",
                "fast_greedy": "🎯 Fast Greedy",
                "ortools": "🔧 OR-Tools (Classic)",
                "simple": "🔄 Simple Fallback",
                
                # Algorithm Descriptions
                "ultra_fast_desc": "Optimized ultra-fast algorithm\n• Typical time: < 0.5 seconds\n• Quality: Very Good\n• Best for: Instant scheduling",
                "smart_greedy_desc": "Intelligent greedy with heuristics\n• Typical time: < 1 second\n• Quality: Excellent\n• Best for: Fast + high quality",
                "ml_inspired_desc": "Pattern-learning algorithm\n• Typical time: 1-3 seconds\n• Quality: Excellent\n• Best for: Learning from data",
                "fast_greedy_desc": "Basic fast greedy algorithm\n• Typical time: < 1 second\n• Quality: Good\n• Best for: Quick results",
                "ortools_desc": "Google's constraint solver\n• Typical time: 10-30 seconds\n• Quality: Optimal\n• Best for: Guaranteed optimality",
                "simple_desc": "Basic fallback algorithm\n• Typical time: < 2 seconds\n• Quality: Good\n• Best for: Compatibility",
                
                # Messages
                "schedule_generated": "Schedule Generated",
                "scheduling_failed": "Scheduling Failed",
                "success_message": "✅ Successfully generated schedule!\n\nAlgorithm: {algorithm}\nTime taken: {time:.2f} seconds\nLessons scheduled: {count}\n\nThe schedule is now displayed in the main window.",
                "error_message": "❌ Failed to generate schedule.\n\nAlgorithm: {algorithm}\nTime taken: {time:.2f} seconds\n\nError: {error}\n\nPlease check your lesson requirements and constraints.",
                "generating_schedule": "Generating Schedule",
                "running_algorithm": "Running {algorithm} algorithm...",
                "initializing": "Initializing...",
                
                # Data Management
                "add": "Add",
                "edit": "Edit", 
                "delete": "Delete",
                "save": "Save",
                "name": "Name",
                "grade_level": "Grade Level",
                "availability": "Availability",
                "needs_lab": "Needs Lab",
                "capacity": "Capacity",
                
                # Common UI
                "close": "Close",
                "ok": "OK",
                "yes": "Yes",
                "no": "No",
                "apply": "Apply",
                "reset": "Reset",
                "refresh": "Refresh",
                "export": "Export",
                "import": "Import",
                "search": "Search",
                "filter": "Filter",
                "clear": "Clear",
                "help": "Help",
                "about": "About",
                "settings": "Settings"
            },
            
            "ar": {
                # Main Window
                "app_title": "مولد جدول المدرسة",
                "view_label": "العرض:",
                "classes": "الفصول",
                "teachers": "المعلمون",
                "generate_schedule": "توليد الجدول",
                
                # Menu Items - Data
                "menu_data": "البيانات",
                "manage_teachers": "إدارة المعلمين",
                "manage_classes": "إدارة الفصول",
                "manage_subjects": "إدارة المواد",
                "manage_rooms": "إدارة الغرف",
                "set_lesson_requirements": "تحديد متطلبات الدروس",
                "teacher_preferences": "تفضيلات المعلمين",
                "teacher_availability": "توفر المعلمين",
                
                # Menu Items - Tools
                "menu_tools": "الأدوات",
                "menu_rules": "القواعد",
                "scheduling_rules": "قواعد الجدولة",
                "constraint_settings": "إعدادات القيود",
                "time_settings": "إعدادات الوقت",
                "database_statistics": "إحصائيات قاعدة البيانات",
                "clear_all_schedules": "مسح جميع الجداول",
                "import_sample_data": "استيراد بيانات تجريبية",
                "backup_database": "نسخ احتياطي لقاعدة البيانات",
                
                # Menu Items - Language
                "menu_language": "اللغة",
                "english": "English",
                "arabic": "العربية",
                
                # Days of week
                "monday": "الاثنين",
                "tuesday": "الثلاثاء",
                "wednesday": "الأربعاء", 
                "thursday": "الخميس",
                "friday": "الجمعة",
                "saturday": "السبت",
                "sunday": "الأحد",
                
                # Time periods
                "period": "الحصة",
                "time_slot": "الفترة الزمنية",
                "free": "فارغ",
                
                # Timetable editing
                "edit": "تحرير",
                "editing": "جاري التحرير",
                "time": "الوقت",
                "current_assignment": "التكليف الحالي:",
                "subject": "المادة",
                "teacher": "المعلم",
                "class": "الفصل",
                "room": "الغرفة",
                "remove_lesson": "إزالة الدرس",
                "move_lesson": "نقل الدرس",
                "move_lesson_title": "نقل الدرس",
                "select_new_time_slot": "اختر الفترة الزمنية الجديدة:",
                "select": "اختيار",
                "current": "الحالي",
                "close": "إغلاق",
                
                # Data management
                "manage": "إدارة",
                "id": "المعرف",
                "name": "الاسم",
                "add": "إضافة",
                "edit": "تحرير",
                "delete": "حذف", 
                "refresh": "تحديث",
                
                # Success/Error Messages
                "success": "نجح",
                "lesson_requirements_generated": "تم إنشاء متطلبات الدروس بنجاح!",
                "all_schedules_cleared": "تم مسح جميع الجداول!",
                "sample_data_imported": "تم استيراد البيانات التجريبية!",
                "backup_created": "تم إنشاء النسخة الاحتياطية",
                "backup_failed": "فشل في إنشاء النسخة الاحتياطية",
                "database_backed_up": "تم نسخ قاعدة البيانات احتياطياً كـ",
                "failed_to_create_backup": "فشل في إنشاء النسخة الاحتياطية",
                
                # Algorithm Selection Dialog
                "select_algorithm": "اختيار خوارزمية الجدولة",
                "choose_algorithm": "اختر خوارزمية الجدولة",
                "generate": "🚀 توليد الجدول",
                "cancel": "❌ إلغاء",
                
                # Algorithm Names
                "ultra_fast": "⚡ فائق السرعة (موصى به)",
                "smart_greedy": "🚀 الجشع الذكي",
                "ml_inspired": "🧠 مجدول مُلهم بالتعلم الآلي",
                "fast_greedy": "🎯 الجشع السريع",
                "ortools": "🔧 OR-Tools (كلاسيكي)",
                "simple": "🔄 البديل البسيط",
                
                # Algorithm Descriptions
                "ultra_fast_desc": "خوارزمية فائقة السرعة محسّنة\n• الوقت المعتاد: أقل من 0.5 ثانية\n• الجودة: جيد جداً\n• الأفضل لـ: الجدولة الفورية",
                "smart_greedy_desc": "الجشع الذكي مع الاستدلال\n• الوقت المعتاد: أقل من ثانية واحدة\n• الجودة: ممتاز\n• الأفضل لـ: السرعة + الجودة العالية",
                "ml_inspired_desc": "خوارزمية تعلم الأنماط\n• الوقت المعتاد: 1-3 ثوانِ\n• الجودة: ممتاز\n• الأفضل لـ: التعلم من البيانات",
                "fast_greedy_desc": "خوارزمية الجشع السريع الأساسية\n• الوقت المعتاد: أقل من ثانية واحدة\n• الجودة: جيد\n• الأفضل لـ: النتائج السريعة",
                "ortools_desc": "حلال القيود من جوجل\n• الوقت المعتاد: 10-30 ثانية\n• الجودة: الأمثل\n• الأفضل لـ: الضمان الأمثل",
                "simple_desc": "خوارزمية بديلة أساسية\n• الوقت المعتاد: أقل من ثانيتين\n• الجودة: جيد\n• الأفضل لـ: التوافق",
                
                # Messages
                "schedule_generated": "تم توليد الجدول",
                "scheduling_failed": "فشل في الجدولة",
                "success_message": "✅ تم توليد الجدول بنجاح!\n\nالخوارزمية: {algorithm}\nالوقت المستغرق: {time:.2f} ثانية\nالدروس المجدولة: {count}\n\nيتم عرض الجدول الآن في النافذة الرئيسية.",
                "error_message": "❌ فشل في توليد الجدول.\n\nالخوارزمية: {algorithm}\nالوقت المستغرق: {time:.2f} ثانية\n\nالخطأ: {error}\n\nيرجى فحص متطلبات الدروس والقيود.",
                "generating_schedule": "توليد الجدول",
                "running_algorithm": "تشغيل خوارزمية {algorithm}...",
                "initializing": "التهيئة...",
                
                # Data Management
                "add": "إضافة",
                "edit": "تعديل",
                "delete": "حذف", 
                "save": "حفظ",
                "name": "الاسم",
                "grade_level": "المستوى الدراسي",
                "availability": "التوفر",
                "needs_lab": "يحتاج مختبر",
                "capacity": "السعة",
                
                # Common UI
                "close": "إغلاق",
                "ok": "موافق",
                "yes": "نعم",
                "no": "لا",
                "apply": "تطبيق",
                "reset": "إعادة تعيين",
                "refresh": "تحديث",
                "export": "تصدير",
                "import": "استيراد",
                "search": "بحث",
                "filter": "فلترة",
                "clear": "مسح",
                "help": "مساعدة",
                "about": "حول",
                "settings": "الإعدادات"
            }
        }
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get translated text for the current language
        
        Args:
            key: Translation key
            **kwargs: Format parameters for the text
            
        Returns:
            Translated text, or the key if translation not found
        """
        try:
            text = self.translations[self.current_language].get(key, key)
            if kwargs:
                return text.format(**kwargs)
            return text
        except (KeyError, ValueError):
            return key
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self.current_language
    
    def is_rtl(self) -> bool:
        """Check if current language is right-to-left"""
        return self.current_language == "ar"
    
    def get_days_of_week(self) -> list:
        """Get localized days of the week"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return [self.get_text(day) for day in days]
    
    def get_font_family(self) -> str:
        """Get appropriate font family for current language"""
        if self.current_language == "ar":
            # Use fonts that support Arabic
            return "Tahoma"  # Good Arabic support on Windows
        return "Helvetica"
    
    def get_text_anchor(self) -> str:
        """Get text anchor for current language (RTL support)"""
        return "e" if self.is_rtl() else "w"

# Global localization instance
_localization = Localization()

def get_localization() -> Localization:
    """Get the global localization instance"""
    return _localization

def t(key: str, **kwargs) -> str:
    """Shortcut function for getting translated text"""
    return _localization.get_text(key, **kwargs)