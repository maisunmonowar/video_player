import argostranslate.package
import argostranslate.translate

class Translator:
    def __init__(self):
        # Update package index on init to ensure we have the latest list
        try:
            argostranslate.package.update_package_index()
            print("Successfully updated argos translate package index.")
        except Exception as e:
            print(f"Could not update index (maybe offline?): {e}")

    def ensure_language_package(self, from_code: str, to_code: str):
        if from_code == to_code:
            return # No translation needed
            
        installed_packages = argostranslate.package.get_installed_packages()
        
        # Check if installed
        for pkg in installed_packages:
            if pkg.from_code == from_code and pkg.to_code == to_code:
                print(f"Translation package {from_code} -> {to_code} already installed.")
                return

        print(f"Downloading translation package {from_code} -> {to_code}...")
        available_packages = argostranslate.package.get_available_packages()
        
        try:
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_code and x.to_code == to_code,
                    available_packages
                )
            )
            argostranslate.package.install_from_path(package_to_install.download())
            print("Package installed successfully.")
        except StopIteration:
            print(f"Error: Could not find translation package for {from_code} -> {to_code}")
            raise ValueError(f"No translation package available for '{from_code}' to '{to_code}'.")

    def translate_segments(self, segments, from_code: str, to_code: str):
        """
        Translates a list of segment dictionaries text to the target language.
        Returns a new list of segments with translated text.
        """
        if from_code == to_code:
            return segments

        self.ensure_language_package(from_code, to_code)
        
        print(f"Translating segments to {to_code}...")
        translated_segments = []
        for segment in segments:
            # Reconstruct the segment
            translated_text = argostranslate.translate.translate(segment["text"], from_code, to_code)
            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": translated_text
            })
        print("Translation complete.")
        return translated_segments
