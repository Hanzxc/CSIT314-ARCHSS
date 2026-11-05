"""Persistence methods for US37, US38 and US46-48. Uses the team's real tables."""
from datetime import date, timedelta
from database.db import getConnection

class IDPAnalytics:
    @staticmethod
    def period_bounds(period, selected_date):
        """Return inclusive start and exclusive end, as date values."""
        try:
            chosen = date.fromisoformat(selected_date)
        except (TypeError, ValueError):
            raise ValueError("Choose a valid date in YYYY-MM-DD format") from None
        if period == "daily":
            start = chosen
            end = chosen + timedelta(days=1)
        elif period == "weekly":
            start = chosen - timedelta(days=chosen.weekday())
            end = start + timedelta(days=7)
        elif period == "monthly":
            start = chosen.replace(day=1)
            end = date(start.year + 1, 1, 1) if start.month == 12 else date(start.year, start.month + 1, 1)
        else:
            raise ValueError("Invalid reporting period")
        return start.isoformat(), end.isoformat()

    def get_designer_statistics(self, designer_id):
        """Include active current and past IDPs with zero counts, scoped to the owner."""
        conn = getConnection()
        try:
            rows = conn.execute("""
                SELECT p.idpId, p.title, p.projectType, p.createdDate,
                       c.categoryName,
                       (SELECT COUNT(*) FROM idp_view v WHERE v.idpId = p.idpId) AS views,
                       (SELECT COUNT(DISTINCT s.customerId) FROM saved_idp s
                        WHERE s.idpId = p.idpId) AS saves
                FROM idp p
                JOIN idp_category c ON c.categoryId = p.categoryId
                WHERE p.designerId = ? AND p.status = 'Active'
                ORDER BY p.createdDate DESC, p.idpId DESC
            """, (designer_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_category_report(self, period, selected_date):
        """Category views and currently saved items saved within the chosen period.

        View history is recorded in idp_view. Deleting a bookmark removes its
        saved_idp row, so these save figures are NOT historical save events.
        """
        start, end = self.period_bounds(period, selected_date)
        start_ts, end_ts = start + ' 00:00:00', end + ' 00:00:00'
        conn = getConnection()
        try:
            rows = conn.execute("""
                SELECT c.categoryId, c.categoryName, c.status,
                    (SELECT COUNT(*) FROM idp p
                     WHERE p.categoryId = c.categoryId AND p.status = 'Active') AS totalIDPs,
                    (SELECT COUNT(*) FROM idp_view v
                     JOIN idp p ON p.idpId = v.idpId
                     WHERE p.categoryId = c.categoryId AND p.status = 'Active'
                     AND v.viewedAt >= ? AND v.viewedAt < ?) AS views,
                    (SELECT COUNT(*) FROM saved_idp s
                     JOIN idp p ON p.idpId = s.idpId
                     WHERE p.categoryId = c.categoryId AND p.status = 'Active'
                     AND s.savedDate >= ? AND s.savedDate < ?) AS saves
                FROM idp_category c
                ORDER BY views DESC, saves DESC, c.categoryName COLLATE NOCASE
            """, (start_ts, end_ts, start_ts, end_ts)).fetchall()
            return {'period': period, 'date': selected_date,
                    'start': start, 'end_exclusive': end,
                    'categories': [dict(r) for r in rows]}
        finally:
            conn.close()

    def list_public_idps(self):
        conn = getConnection()
        try:
            return [dict(r) for r in conn.execute("""
                SELECT p.idpId, p.title, p.description, p.projectType,
                       c.categoryName, u.fullName AS designerName
                FROM idp p
                JOIN idp_category c ON c.categoryId = p.categoryId
                JOIN user_account u ON u.userId = p.designerId
                WHERE p.status = 'Active' AND c.status = 'Active'
                ORDER BY p.createdDate DESC, p.idpId DESC
            """).fetchall()]
        finally:
            conn.close()

    def record_project_view(self, idp_id):
        """Count one request to a real active project; never accept a caller-supplied count."""
        conn = getConnection()
        try:
            cursor = conn.execute("""
                INSERT INTO idp_view(idpId)
                SELECT p.idpId FROM idp p
                JOIN idp_category c ON c.categoryId = p.categoryId
                WHERE p.idpId = ? AND p.status = 'Active' AND c.status = 'Active'
            """, (idp_id,))
            if cursor.rowcount != 1:
                conn.rollback()
                return None
            row = conn.execute("""
                SELECT p.idpId,p.title,p.description,p.location,p.projectType,
                       c.categoryName,u.fullName AS designerName
                FROM idp p
                JOIN idp_category c ON c.categoryId = p.categoryId
                JOIN user_account u ON u.userId=p.designerId
                WHERE p.idpId = ?
            """, (idp_id,)).fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            conn.close()
