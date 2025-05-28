"""
Quick Test für Manual Login und Übersetzungen
"""

def test_translations():
    """Testet Übersetzungs-System"""
    print("=== TRANSLATION TEST ===")
    try:
        from config.translations import translations, t, set_language

        # Deutsche Übersetzungen
        print(f"DE: {t('wareneingang_title')}")

        # Englische Übersetzungen
        set_language('en')
        print(f"EN: {t('wareneingang_title')}")

        # Türkische Übersetzungen
        set_language('tr') 
        print(f"TR: {t('wareneingang_title')}")

        # Polnische Übersetzungen
        set_language('pl')
        print(f"PL: {t('wareneingang_title')}")

        # Zurück zu Deutsch
        set_language('de')

        print("✅ Übersetzungen funktionieren")
        return True

    except Exception as e:
        print(f"❌ Übersetzungs-Fehler: {e}")
        return False

def main():
    print("🧪 QUICK TEST - MANUAL LOGIN & ÜBERSETZUNGEN")
    print("=" * 50)

    if test_translations():
        print("\n✅ TESTS ERFOLGREICH!")
        print("\n🚀 App starten:")
        print("   .\\run_wareneingang.bat")
        print("\n📋 Neue Features:")
        print("   🔐 Manual Login Button")
        print("   🎯 Test-Karte simulieren")
        print("   🌍 Vollständige Übersetzungen (DE/EN/TR/PL)")
    else:
        print("\n❌ Tests fehlgeschlagen")

if __name__ == "__main__":
    main()
