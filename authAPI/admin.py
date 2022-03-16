from django.contrib import admin
from authAPI.models import UserAccount
from django.contrib import messages
from django.http import HttpResponseRedirect
import uuid
# Register your models here.
# Register out own model admin, based on the default UserAdmin
from django.contrib.auth import get_user_model

@admin.register(UserAccount)
class CustomUserAdmin(admin.ModelAdmin):
    list_per_page = 15     
    search_fields = ('first_name','last_name', 'email')
    list_filter = ("is_active", 'is_staff')    
    list_display = ('email',"is_active", 'is_staff')
    readonly_fields = ('last_name', 'first_name', 'is_active', 'is_staff')
    fieldsets = [
        ('Dados assinatura', {'fields': ['email', 'last_name', 'first_name', 'is_active', 'is_staff'],'classes': ['npm']})
    ]

    def fullname(self, obj):
        return obj.get_full_name

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('email',)
        return self.readonly_fields


    def response_change(self, request, obj):
        print(request.POST)
        if "_usercreate" in request.POST:
            # try:
            print('csnackaljs')
            pwd = str(uuid.uuid4())
            obj.objects.create_user(obj.email, pwd)

            self.message_user(request, "Usuário Criado")
            # else:    
            # # except:
            #     self.message_user(request, "Erro ao criar", level=messages.ERROR)

            return HttpResponseRedirect(".") 

        return super().response_change(request, obj)   