from rest_framework.routers import DefaultRouter
from .views import InfoPageViewSet

router = DefaultRouter()
router.register(r'info-pages', InfoPageViewSet, basename='info-pages')
urlpatterns = router.urls

