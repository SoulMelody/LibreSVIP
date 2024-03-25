from libresvip.utils import translation

translation.singleton_translation = translation.get_translation()
translation.singleton_translation.install()
