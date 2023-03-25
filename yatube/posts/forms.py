import re

from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        text = self.cleaned_data['text']
        stop_words = ['мат', 'война']
        for word in stop_words:
            if re.search(r'\b{}\b'.format(word), text.lower()):
                raise forms.ValidationError(
                    f'Слово "{word}" запрещено в тексте поста')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    text = forms.CharField(
        max_length=200,
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control mb-2',
            'placeholder': 'Введите ваш комментарий',
            'rows': 3,
        })
    )
