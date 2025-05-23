from aplication.security.models import Permission
from aplication.security.models import User, Group


class GroupPermission:

    @staticmethod
    def get_permission_dict_of_group(user: User):
        if user.is_superuser:
            permissions = list(Permission.objects.all().values_list('codename', flat=True))
            permissions = {x: x for x in permissions if x not in (None, '')}
        else:
            print("usuario=>", user)
            group = user.get_group_session()
            if group:  # Si el grupo es válido, obtiene los permisos del grupo.
                permissions = list(
                    group.groupmodulepermission_set.all().values_list('permissions__codename', flat=True)
                )
                permissions = {x: x for x in permissions if x not in (None, '')}
            else:
                permissions = {}
        return permissions
