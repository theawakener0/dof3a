from rest_framework_nested import routers
from .views import StudentViewSet, PostViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
router.register(r'posts', PostViewSet, basename='posts')

post_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
post_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = router.urls + post_router.urls