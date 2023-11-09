from django.urls import path
from . import views
urlpatterns = [

    # genai paths
    # path('document_extraction', views.document_extraction,name='document_extraction'),
    path('document_extraction/upload_document', views.upload_document,name='document_extraction_upload_document'),
    path('document_extraction/parser_setup', views.parser_setup,name='document_extraction_parser_setup'),
    path('document_extraction/extraction_process', views.extraction_process,name='document_extraction_extraction_process'),
    
    # DOCUMENT EXTRACTION - UPLOAD DOCUMENT
    path('document_extraction/ud_action_newdoc', views.de_ud_action_newdoc,name='document_extraction'),
    path('document_extraction/ud_action_docname', views.de_ud_action_docname,name='document_extraction'),
    path('document_extraction/ud_action_docdel', views.de_ud_action_docdel,name='document_extraction'),
    path('document_extraction/ud_action_showconf', views.de_ud_action_showconf,name='document_extraction'),
    path('document_extraction/ud_action_search', views.de_ud_action_search,name='document_extraction'),

    # DOCUMENT EXTRACTION - PARSER SETUP
    path('document_extraction/ps_action_view', views.de_ps_action_view,name='document_extraction'),
    path('document_extraction/ps_action_parser', views.de_ps_action_parser,name='document_extraction'),
    path('document_extraction/ps_action_del', views.de_ps_action_del,name='document_extraction'),
    path('document_extraction/ps_action_save', views.de_ps_action_save,name='document_extraction'),
    path('document_extraction/ps_action_test', views.de_ps_action_test,name='document_extraction'),
    path('document_extraction/ps_action_update', views.de_ps_action_update,name='document_extraction'),
    path('document_extraction/ps_action_showconf', views.de_ps_action_showconf,name='document_extraction'),

    # DOCUMENT EXTRACTION - EXTRACTION PROCESS
    path('document_extraction/ep_action_downjson/<id>', views.de_ep_action_downjson,name='document_extraction'),
    path('document_extraction/ep_action_downcsv/<id>', views.de_ep_action_downcsv,name='document_extraction'),
    path('document_extraction/ep_action_alldoc/<id>', views.de_ep_action_alldoc,name='document_extraction'),



    path('document_translation', views.document_translation,name='document_translation'),

    # DOCUMENT TRANSLATION
    path('document_translation/action_newdoc', views.dt_action_newdoc,name='aksi-upload-new-doc'),
    path('document_translation/action_docname', views.dt_action_docname,name='aksi-klik-doc-name'),
    path('document_translation/action_docdel', views.dt_action_docdel,name='aksi=klik-del-step2'),
    path('document_translation/action_showconf', views.dt_action_showconf,name='document_translation'),

    path('bank_statement', views.bank_statement,name='bank_statement'),
    path('bank_statement/action_newdoc', views.bs_action_newdoc,name='aksi-upload-new-doc'),
    path('bank_statement/action_docname', views.bs_action_docname,name='aksi-klik-doc-name'),
    path('bank_statement/action_docdel', views.bs_action_docdel,name='aksi-klik-del-step2'),
    path('bank_statement/action_process', views.bs_action_processfp,name='aksi-klik-process-free-prompt'),

    path('ktp_extraction', views.ktp_extraction,name='ktp_extraction'), 
    path('ktp_extraction/action_newdoc', views.ke_action_newdoc,name='aksi-upload-newdoc'),
    path('ktp_extraction/action_docname', views.ke_action_docname,name='aksi-klik-docname-listdoc'),
    path('ktp_extraction/action_docdel', views.ke_action_docdel,name='aksi-klik-del-listdoc'),
    path('ktp_extraction/action_showconf', views.ke_action_showconf,name='aksi-show-the-confidence'),
    path('ktp_extraction/action_extract', views.ke_action_extract,name='aksi-extract-entity'),

    path('image_extraction', views.image_extraction,name='image_extraction'),
    path('image_extraction/action_newdoc', views.ie_action_newdoc,name='aksi-upload-newdoc'),
    path('image_extraction/action_docname', views.ie_action_docname,name='aksi-klik-docname-listdoc'),
    path('image_extraction/action_docdel', views.ie_action_docdel,name='aksi-klik-del-listdoc'),
    path('image_extraction/action_showconf', views.ie_action_showconf,name='aksi-show-the-confidence'),
    path('image_extraction/action_search', views.ie_action_search,name='aksi-search'),

    # dashboard paths

    path('', views.indexPage,name='indexPage'),
    path('dashboard_default', views.dashboard_default,name='index'),
    path('dashboard_ecommerce', views.dashboard_ecommerce,name='dashboard_ecommerce'),
    path('dashboard_project', views.dashboard_project,name='dashboard_project'),



    # [start] TEMPLATE PATHS

    # page layout paths

    path('page_layout_boxed',views.page_layout_boxed,name='page_layout_boxed'),
    path('page_layout_rtl',views.page_layout_rtl,name='page_layout_rtl'),
    path('page_layout_dark',views.page_layout_dark,name='page_layout_dark'),
    path('page_layout_footer_light',views.page_layout_footer_light,name='page_layout_footer_light'),
    path('page_layout_footer_dark',views.page_layout_footer_dark,name='page_layout_footer_dark'),
    path('page_layout_footer_fixed',views.page_layout_footer_fixed,name='page_layout_footer_fixed'),
    
    # chat paths

    path('chat_chat_app',views.chat_chat_app,name='chat_chat_app'),
    path('chat_video_chat',views.chat_video_chat,name='chat_video_chat'),

    # users paths

    path('users_users_profile',views.users_users_profile,name='users_users_profile'),
    path('users_users_edit',views.users_users_edit,name='users_users_edit'),
    path('users_users_card',views.users_users_card,name='users_users_card'),

    # to do path

    path('to_do_design',views.to_do_design,name='to_do_design'),
    path('to_do_database',views.to_do_database,name='to_do_database'),
    path('delete/<str:pk>/', views.deleteTask, name="delete"),
    path('updateTask/<str:pk>/', views.updateTask,name='updateTask'),
    path('markAllComplete/', views.markAllComplete, name='markAllComplete'),
    path('markAllIncomplete/', views.markAllIncomplete, name='markAllIncomplete'),
    

    # sample page path

    path('sample_page',views.sample_page,name='sample_page'),

    # others path
    # error pages

    path('error_page_1',views.error_page_1,name='error_page_1'),
    path('error_page_2',views.error_page_2,name='error_page_2'),
    path('error_page_3',views.error_page_3,name='error_page_3'),
    path('error_page_4',views.error_page_4,name='error_page_4'),

    # authentication paths

    path('login',views.login_simple,name='login'),
    path('login_simple',views.login_simple,name='login_simple'),
    path('login_with_bg_image',views.login_with_bg_image,name='login_with_bg_image'),
    path('login_with_image_two',views.login_with_image_two,name='login_with_image_two'),
    path('login_with_validation',views.login_with_validation,name='login_with_validation'),
    path('login_with_tooltip',views.login_with_tooltip,name='login_with_tooltip'),
    path('login_with_sweetalert',views.login_with_sweetalert,name='login_with_sweetalert'),
    path('register_simple',views.register_simple,name='register_simple'),
    path('register_with_bg_image',views.register_with_bg_image,name='register_with_bg_image'),
    path('register_with_bg_video',views.register_with_bg_video,name='register_with_bg_video'),
    path('unlock_user',views.unlock_user,name='unlock_user'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('create_password',views.create_password,name='create_password'),
    path('maintenance',views.maintenance,name='maintenance'),
    path('logout_view',views.logout_view,name='logout_view'),


    # coming soon paths

    path('coming_simple',views.coming_simple,name='coming_simple'),
    path('coming_with_bg_image',views.coming_with_bg_image,name='coming_with_bg_image'),
    path('coming_with_bg_video',views.coming_with_bg_video,name='coming_with_bg_video'),


    # faq path

    path('faq',views.faq,name='faq'),


    # support ticket path

    path('support_ticket',views.support_ticket,name='support_ticket'),

    # documentation

    path('documentation_accordian',views.documentation_accordian,name='documentation_accordian'),
    path('documentation_app',views.documentation_app,name='documentation_app'),
    path('documentation_change_log',views.documentation_change_log,name='documentation_change_log'),
    path('documentation_component',views.documentation_component,name='documentation_component'),
    path('documentation_customer_review',views.documentation_customer_review,name='documentation_customer_review'),
    path('documentation_feature_list',views.documentation_feature_list,name='documentation_feature_list'),
    path('documentation_getting_started',views.documentation_getting_started,name='documentation_getting_started'),
    path('documentation_index',views.documentation_index,name='documentation_index'),
    path('documentation_layout_setting',views.documentation_layout_setting,name='documentation_layout_setting'),
    path('documentation_options',views.documentation_options,name='documentation_options'),
    path('documentation_tree',views.documentation_tree,name='documentation_tree'),

    # django documentation paths

    path('documentation_django_to_do',views.documentation_django_to_do,name='documentation_django_to_do'),
    path('documentation_django_authentication',views.documentation_django_authentication,name='documentation_django_authentication'),
    path('documentation_django_customizer',views.documentation_django_customizer,name='documentation_django_customizer'),
    path('documentation_django_options',views.documentation_django_options,name='documentation_django_options'),
    path('documentation_django_components',views.documentation_django_components,name='documentation_django_components'),
    path('documentation_django_getting_started',views.documentation_django_getting_started,name='documentation_django_getting_started'),
    path('documentation_django_tree',views.documentation_django_tree,name='documentation_django_tree'),
    path('documentation_django_app',views.documentation_django_app,name='documentation_django_app'),
    
    # [end] TEMPLATE PATHS

    path('bonus_ui_sweet_alert2',views.bonus_ui_sweet_alert2,name='bonus_ui_sweet_alert2'),
]