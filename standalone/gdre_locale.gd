class_name GDRELocale
extends RefCounted

enum InterfaceLanguage {
	SYSTEM_DEFAULT,
	ENGLISH,
	SIMPLIFIED_CHINESE,
}

static func apply_selected() -> void:
	var selected_language := int(GDREConfig.get_setting("interface_language"))
	match selected_language:
		InterfaceLanguage.ENGLISH:
			TranslationServer.set_locale("en")
		InterfaceLanguage.SIMPLIFIED_CHINESE:
			TranslationServer.set_locale("zh_CN")
		_:
			TranslationServer.set_locale(OS.get_locale())
