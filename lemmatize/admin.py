from django.contrib import admin

# Register your models here.
from .models import Lemma, LemmaMeet


@admin.register(Lemma)
class LemmaAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('id', 'name', 'meets_count')
    search_fields = ('name', )


@admin.register(LemmaMeet)
class LemmaMeetAdmin(admin.ModelAdmin):
    fields = ('lemma', 'timestamp', 'post')
    list_display = ('lemma', 'timestamp', 'post_text')

    search_fields = ('timestamp', )
