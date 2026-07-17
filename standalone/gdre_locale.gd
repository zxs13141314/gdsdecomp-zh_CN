class_name GDRELocale
extends RefCounted

const SETTING_NAME := "General/interface_language"

enum InterfaceLanguage {
	SYSTEM_DEFAULT,
	ENGLISH,
	SIMPLIFIED_CHINESE,
}

static func apply_selected() -> void:
	var selected_language := int(GDREConfig.get_setting(SETTING_NAME))
	match selected_language:
		InterfaceLanguage.ENGLISH:
			TranslationServer.set_locale("en")
		InterfaceLanguage.SIMPLIFIED_CHINESE:
			TranslationServer.set_locale("zh_CN")
		_:
			TranslationServer.set_locale(OS.get_locale())
