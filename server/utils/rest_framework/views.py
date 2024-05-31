from rest_framework import viewsets


class BaseViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, editor=self.request.user)
