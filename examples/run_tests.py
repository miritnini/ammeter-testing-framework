from src.testing.test_framework import AmmeterTestFramework

def main():
    # יצירת מסגרת הבדיקות
    framework = AmmeterTestFramework()
    # הרצת בדיקות לכל סוגי האמפרמטרים
    #ammeter_types = ["greenlee", "entes", "circutor"]
    results = {}
    
    for ammeter_type in framework.devices.keys():
        print(f"Testing {ammeter_type} ammeter...")
        result = framework.run_test(ammeter_type)
        results[ammeter_type] = result

    # השוואת תוצאות
   # for ammeter_type, result in results.items():
    #    print(f"\nResults for {ammeter_type}:")
    #   print(result)

    #return results
    print("\nSUMMARY:")
    for name, res in results.items():
        print(f"{name}: PASS={res.get('test_passed', False)}")

if __name__ == "__main__":
    main() 