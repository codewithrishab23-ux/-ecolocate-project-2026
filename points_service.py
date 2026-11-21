"""
Points Management and Wallet Service for EcoLocate
Handles repeat submission points calculation, wallet balance management,
transaction ledger recording, and admin adjustments.
"""

from db import execute_query

def calculate_points_for_quantity(accepted_quantity):
    """
    Query active points_tiers dynamically from the database to determine
    the points earned for a given verified accepted quantity of e-waste items.
    
    If quantity <= 0, returns 0.
    Dynamically respects admin-configured tiers without hardcoding.
    """
    if not accepted_quantity or accepted_quantity <= 0:
        return 0
    
    tier = execute_query(
        """
        SELECT points_awarded FROM points_tiers
        WHERE is_active = 1
          AND min_quantity <= %s
          AND (max_quantity >= %s OR max_quantity IS NULL)
        ORDER BY min_quantity DESC
        LIMIT 1
        """,
        (accepted_quantity, accepted_quantity),
        fetchone=True
    )
    if tier and tier.get('points_awarded') is not None:
        return int(tier['points_awarded'])
    
    # Fallback to default structure if no matching tier found
    if accepted_quantity == 1:
        return 5
    elif accepted_quantity == 2:
        return 15
    elif 3 <= accepted_quantity <= 4:
        return 25
    elif 5 <= accepted_quantity <= 9:
        return 40
    else:
        return 60


def get_active_points_tiers():
    """Retrieve all points tiers ordered by min_quantity."""
    return execute_query(
        "SELECT * FROM points_tiers ORDER BY min_quantity ASC",
        fetchall=True
    ) or []


def save_points_tier(tier_name, min_quantity, max_quantity, points_awarded, is_active=1, tier_id=None):
    """Create or update a points tier dynamically."""
    if tier_id:
        execute_query(
            """
            UPDATE points_tiers
            SET tier_name = %s, min_quantity = %s, max_quantity = %s, points_awarded = %s, is_active = %s
            WHERE id = %s
            """,
            (tier_name, min_quantity, max_quantity, points_awarded, is_active, tier_id),
            commit=True
        )
        return tier_id
    else:
        new_id = execute_query(
            """
            INSERT INTO points_tiers (tier_name, min_quantity, max_quantity, points_awarded, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (tier_name, min_quantity, max_quantity, points_awarded, is_active),
            commit=True
        )
        return new_id


def get_or_create_wallet(user_id):
    """
    Retrieve user points wallet, or create an initial 0-balance wallet if none exists.
    """
    if not user_id:
        return None
    
    wallet = execute_query(
        "SELECT * FROM user_points_wallets WHERE user_id = %s",
        (user_id,),
        fetchone=True
    )
    if not wallet:
        execute_query(
            """
            INSERT INTO user_points_wallets (user_id, total_earned, total_redeemed, current_balance, pending_points)
            VALUES (%s, 0, 0, 0, 0)
            """,
            (user_id,),
            commit=True
        )
        wallet = execute_query(
            "SELECT * FROM user_points_wallets WHERE user_id = %s",
            (user_id,),
            fetchone=True
        )
    return wallet


def get_wallet_ledger(user_id):
    """Return all transactions for a user's wallet in reverse chronological order."""
    if not user_id:
        return []
    return execute_query(
        """
        SELECT pt.*, a.username AS admin_username, s.submission_code
        FROM points_transactions pt
        LEFT JOIN admins a ON pt.created_by_admin_id = a.id
        LEFT JOIN ewaste_submissions s ON pt.submission_id = s.id
        WHERE pt.user_id = %s
        ORDER BY pt.created_at DESC, pt.id DESC
        """,
        (user_id,),
        fetchall=True
    ) or []


def recalculate_wallet_balance(user_id):
    """
    Recalculate wallet balance from transaction ledger to guarantee 100% ledger consistency.
    """
    if not user_id:
        return 0
    wallet = get_or_create_wallet(user_id)
    if not wallet:
        return 0

    totals = execute_query(
        """
        SELECT 
            COALESCE(SUM(points_amount), 0) AS calculated_balance,
            COALESCE(SUM(CASE WHEN points_amount > 0 THEN points_amount ELSE 0 END), 0) AS total_earned,
            COALESCE(SUM(CASE WHEN points_amount < 0 THEN ABS(points_amount) ELSE 0 END), 0) AS total_redeemed
        FROM points_transactions
        WHERE user_id = %s
        """,
        (user_id,),
        fetchone=True
    )
    calc_bal = totals['calculated_balance'] if totals else 0
    tot_earned = totals['total_earned'] if totals else 0
    tot_redeemed = totals['total_redeemed'] if totals else 0

    execute_query(
        """
        UPDATE user_points_wallets
        SET current_balance = %s, total_earned = %s, total_redeemed = %s
        WHERE user_id = %s
        """,
        (calc_bal, tot_earned, tot_redeemed, user_id),
        commit=True
    )
    return calc_bal


def award_submission_points(submission_id, admin_id=None, manual_points=None, reason=None):
    """
    Verify items and award points for an ewaste submission.
    
    Guards:
    - Points cannot be awarded more than once for the same submission (duplicate prevention).
    - Points calculated dynamically based on accepted_quantity of verified items.
    - If manual_points is passed, manual reason is strictly required.
    - Updates points_transactions ledger and user_points_wallets balance.
    """
    submission = execute_query(
        "SELECT * FROM ewaste_submissions WHERE id = %s",
        (submission_id,),
        fetchone=True
    )
    if not submission:
        return False, "Submission not found.", 0

    # Strict duplicate points claim prevention
    if submission.get('points_approved'):
        return False, f"Points have already been awarded for submission {submission['submission_code']}.", 0

    # Sum verified accepted items (excluding rejected or 0-quantity items)
    items_sum = execute_query(
        """
        SELECT 
            COALESCE(SUM(accepted_quantity), 0) AS total_accepted,
            COALESCE(SUM(submitted_quantity), 0) AS total_submitted
        FROM ewaste_submission_items
        WHERE submission_id = %s AND status != 'rejected'
        """,
        (submission_id,),
        fetchone=True
    )
    total_accepted = int(items_sum['total_accepted']) if items_sum else 0
    total_submitted = int(items_sum['total_submitted']) if items_sum else 0

    # Calculate points via active tiers
    calculated_pts = calculate_points_for_quantity(total_accepted)

    if manual_points is not None:
        try:
            final_points = int(manual_points)
            if final_points < 0:
                return False, "Points awarded cannot be negative.", 0
        except (ValueError, TypeError):
            return False, "Invalid manual points value.", 0

        if final_points != calculated_pts and not (reason and str(reason).strip()):
            return False, "A mandatory reason is required when manually overriding points.", 0
    else:
        final_points = calculated_pts

    # Update submission record
    execute_query(
        """
        UPDATE ewaste_submissions
        SET total_accepted_items = %s,
            points_calculated = %s,
            points_awarded = %s,
            points_approved = 1,
            points_approved_at = NOW(),
            points_approved_by = %s,
            status = 'verified',
            manual_adjustment_reason = %s
        WHERE id = %s
        """,
        (
            total_accepted,
            calculated_pts,
            final_points,
            admin_id,
            reason.strip() if reason else None,
            submission_id
        ),
        commit=True
    )

    # If linked to a registered user, record in wallet and ledger
    user_id = submission.get('user_id')
    if user_id:
        wallet = get_or_create_wallet(user_id)
        current_bal = int(wallet.get('current_balance', 0))
        new_bal = current_bal + final_points

        tx_reason = f"Points awarded for submission {submission['submission_code']} ({total_accepted} accepted item(s))"
        if reason and str(reason).strip():
            tx_reason += f" - Note: {str(reason).strip()}"

        execute_query(
            """
            INSERT INTO points_transactions (
                wallet_id, user_id, submission_id, transaction_type,
                points_amount, balance_after, reason, created_by_admin_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                wallet['id'],
                user_id,
                submission_id,
                'submission_reward',
                final_points,
                new_bal,
                tx_reason,
                admin_id
            ),
            commit=True
        )

        # Recalculate to ensure absolute ledger consistency
        recalculate_wallet_balance(user_id)

    return True, f"Successfully awarded {final_points} points for submission {submission['submission_code']}.", final_points


def manual_adjust_points(user_id, points_delta, reason, admin_id=None):
    """
    Allow administrator to manually credit or debit points with a mandatory reason.
    Strictly forbids empty reasons and prevents balance from falling below 0.
    """
    if not user_id:
        return False, "User ID is required."
    
    if not reason or not str(reason).strip():
        return False, "A mandatory explanation reason is required for manual points adjustment."

    try:
        delta = int(points_delta)
    except (ValueError, TypeError):
        return False, "Invalid points adjustment amount."

    if delta == 0:
        return False, "Points adjustment amount cannot be zero."

    wallet = get_or_create_wallet(user_id)
    current_bal = int(wallet.get('current_balance', 0))
    new_bal = current_bal + delta

    if new_bal < 0:
        return False, f"Adjustment would cause negative balance ({new_bal}). Current balance is {current_bal}."

    tx_type = 'manual_credit' if delta > 0 else 'manual_debit'

    execute_query(
        """
        INSERT INTO points_transactions (
            wallet_id, user_id, submission_id, transaction_type,
            points_amount, balance_after, reason, created_by_admin_id
        ) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s)
        """,
        (
            wallet['id'],
            user_id,
            tx_type,
            delta,
            new_bal,
            str(reason).strip(),
            admin_id
        ),
        commit=True
    )

    recalculate_wallet_balance(user_id)
    return True, f"Successfully adjusted points by {delta:+d} points."
