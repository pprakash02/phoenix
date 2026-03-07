# legacy_workspace/legacy_billing.py
import sys


def process_transaction(amount):
    """Undocumented legacy function written 10 years ago."""
    val = float(amount)

    # Hidden Bug 1: Fails on negative numbers
    if val < 0:
        raise ValueError("Transaction amount cannot be negative.")

    # Hidden Bug 2: ZeroDivisionError if amount is exactly 0
    if val == 0:
        return 100 / 0

    return val * 1.05


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("CRITICAL: Missing transaction amount argument.")
        sys.exit(1)

    print("--- LEGACY BILLING ENGINE V1.4 ---")
    input_amount = sys.argv[1]
    print(f"Processing transaction for input: {input_amount}")

    final_total = process_transaction(input_amount)
    print(f"SUCCESS: Final Total (w/ tax): ${final_total:.2f}")