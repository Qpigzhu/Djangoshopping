from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'
    verbose_name = "操作管理"

    #信号向量
    def ready(self):
        import user_operation.signals