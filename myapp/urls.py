

from django.urls import path
from . import views
urlpatterns = [

    path('',views.loginget),
    path('login_post/',views.login_post),
    path('admin_home/',views.admin_home),
    path('verify_expert/',views.verify_expert),
    path('verify_expert_accept/<id>',views.verify_expert_accept),
    path('verify_expert_reject/<id>',views.verify_expert_reject),
    path('sendreply/<id>/',views.sendreply),
    path('view_complaint/',views.view_complaint),
    path('view_users/',views.view_users),
    path('view_feedback/',views.view_feedback),
    path('change_password/',views.change_password),
    path('changepassword/',views.changepassword),
    path('admin_view_post/',views.admin_view_post),
    path('view_expert_review/',views.view_expert_review),



    path('expert_registration/',views.expert_registration),
    path('expert_registration_post/',views.expert_registration_post),
    path('expert_add_guideline/',views.expert_add_guideline),
    path('expert_add_guideline_post/',views.expert_add_guideline_post),
    path('expert_add_tips/',views.expert_add_tips),
    path('expert_edit_profile/',views.expert_edit_profile),
    path('expert_view_guideline/',views.expert_view_guideline),
    path('expert_view_profile/',views.expert_view_profile),
    path('expert_view_tips/',views.expert_view_tips),
    path('expert_home/',views.expert_home),
    path('expert_add_tips_post/',views.expert_add_tips_post),
    path('expert_update_tips_post/',views.expert_update_tips_post),
    path('expert_edit_tips/<id>',views.expert_edit_tips),
    path('expert_delete_tips/<id>',views.expert_delete_tips),
    path('expert_delete_guideline/<id>', views.expert_delete_guideline),
    path('expert_edit_guideline/<id>', views.expert_edit_guideline),
    path('expert_update_guideline_post/',views.expert_update_guideline_post),
    path('expert_update_profile_post/',views.expert_update_profile_post),




    path("android_login/",views.android_login),
    path("android_login1/",views.android_login1),
    path("veryfy_user/",views.veryfy_user),
    path("android_user_registration/",views.android_user_registration),
    path("insert_complaint/",views.insert_complaint),
    path("insert_feedback/",views.insert_feedback),
    path("insert_review/",views.insert_review),
    path("insert_post/",views.insert_post),
    path("insert_like/",views.insert_like),
    path("Friend_requests/",views.Friend_requests),
    path("view_image_notification/",views.view_image_notification),
    path("user_viewreply/",views.user_viewreply),

    path("view_expert/",views.view_expert),
    path("view_shared_content/",views.view_shared_content),
    path("view_feedback_content/",views.view_feedback_content),
    path("view_parants/",views.view_parants),
    path("view_post/",views.view_post),
    path("view_reply/",views.view_reply),
    path("view_review/",views.view_review),
    path("post_insert/",views.post_insert),
    path("my_post/",views.my_post),
    path("view_my_post/",views.view_my_post),
    path("view_comment/",views.view_comment),
    path("add_comment/",views.add_comment),





    #############################################
    path("reg_view_student/",views.reg_view_student),
    path("parent_registration/",views.parent_registration),
    path("view_otherusers/",views.view_otherusers),
    path("accept_notification/",views.accept_notification),
    path("reject_notification/",views.reject_notification),
    path("send_request/",views.send_request),
    path("view_request/",views.view_request),
    path("accept_request/",views.accept_request),
    path("reject_request/",views.reject_request),
    path("view_myFriends/",views.view_myFriends),
    path("flut_view_chat/",views.flut_view_chat),
    path("flut_send_chat/",views.flut_send_chat),
    path("android_like/",views.android_like),
    path("share_post/",views.share_post),
    path("delete_post/",views.delete_post),
    path("ViewSharedPost/",views.ViewSharedPost),
    path("UserViewTips/",views.UserViewTips),
    path("user_view_review/",views.user_view_review),
    path("ShareUserAccount/",views.ShareUserAccount),
    path("view_myFriends_for_share/",views.view_myFriends_for_share),
    path("send_view_shared_details/",views.send_view_shared_details),

    path("parent_view_post/",views.parent_view_post),
    path("parent_view_activity/",views.parent_view_activity),
    path("user_profile/",views.user_profile),
    path("update_profile/",views.update_profile),

    path('get_user_profile/', views.get_user_profile, name='get_user_profile'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('clear_face_pickles/', views.clear_face_pickles, name='clear_face_pickles'),

]