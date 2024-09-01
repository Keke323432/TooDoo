from django.apps import AppConfig


class TodoProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todo_project'
    
    def ready(self):
        import todo_project.signals  # Ensure signals are imported

 