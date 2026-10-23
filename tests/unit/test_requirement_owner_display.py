"""Synthetic scoped owner regression; also runnable with stdlib unittest."""
import unittest
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import Session
from app.schemas.requirement_center import RequirementCenterIssue
from app.services.requirement_center import _owner_key, _owner_name, _resolve_issue_owners


def card(owner):
    return RequirementCenterIssue(id="REQ-9000", type="requirement", title="合成样本", owner=_owner_name(owner),
        owner_key=_owner_key(owner), source="capture", stage="capture", detail_url="", updated_at="")


class OwnerDisplayTests(unittest.TestCase):
    def test_safe_offline_fallback(self):
        for value, expected in [(None,"未分配"),("  ","未分配"),("null","未分配"),("None","未分配"),
                ("product","产品团队"),("user","用户反馈"),("研发团队","研发团队"),("历史导入团队","历史导入团队"),
                ("user_synthetic_missing","未知用户")]:
            with self.subTest(value=value):
                issue=card(value)
                _resolve_issue_owners([issue], None, None)
                self.assertEqual(issue.owner, expected)
                self.assertEqual(issue.owner_display_name, expected)
                self.assertEqual(issue.owner_key, _owner_key(value))

    def test_cards_keep_raw_keys_before_safe_display(self):
        import tempfile
        from pathlib import Path
        from app.services.requirement_center import _build_issue, using_governance_root
        with tempfile.TemporaryDirectory() as directory, using_governance_root(Path(directory)):
            for kind, prefix in [("requirement", "REQ"), ("bug", "BUG")]:
                issue = _build_issue(kind, {"id":f"{prefix}-9100-synthetic", "owner":"user_sample", "status":"captured"})
                self.assertEqual(issue.owner_key, "user_sample")
                self.assertEqual(issue.owner, "未知用户")

    def test_scoped_batch_names_and_identity(self):
        engine=create_engine("sqlite://")
        with Session(engine) as db:
            db.execute(text("CREATE TABLE admin_users (id TEXT, nickname TEXT, username TEXT, status TEXT, deleted_at TEXT)"))
            db.execute(text("CREATE TABLE admin_spaces (id TEXT, owner_id TEXT, deleted_at TEXT)"))
            db.execute(text("CREATE TABLE admin_space_members (space_id TEXT, user_id TEXT)"))
            users=[("user_owner","同名","owner","正常",None), ("user_member","同名","member","正常",None),
                ("user_username","  ","readable","正常",None), ("user_empty",None,"user_empty","正常",None),
                ("user_outside","秘密名称","outside","正常",None), ("user_deleted","删除名称","deleted","已删除",None),
                ("user_softdeleted","删除名称","deleted2","正常","2026-01-01")]
            db.execute(text("INSERT INTO admin_users VALUES (:id,:nickname,:username,:status,:deleted_at)"),
                [dict(zip(["id","nickname","username","status","deleted_at"],row)) for row in users])
            db.execute(text("INSERT INTO admin_spaces VALUES ('space_a','user_owner',NULL),('space_b','user_outside',NULL)"))
            db.execute(text("INSERT INTO admin_space_members VALUES ('space_a',:user)"),[{"user":u[0]} for u in users if u[0] not in {"user_owner","user_outside"}])
            statements=[]
            event.listen(engine,"before_cursor_execute",lambda conn,cursor,statement,parameters,context,many: statements.append(statement))
            issues=[card(u[0]) for u in users]+[card("user_missing"), card("user_owner")]
            _resolve_issue_owners(issues,db,"space_a")
            self.assertEqual([i.owner for i in issues],["同名","同名","readable","未知用户","未知用户","未知用户","未知用户","未知用户","同名"])
            self.assertNotEqual(issues[0].owner_key, issues[1].owner_key)
            self.assertEqual(len(statements),1)
            self.assertTrue(statements[0].lstrip().startswith("SELECT"))
            _resolve_issue_owners(issues,db,"space_b")
            self.assertEqual(issues[0].owner,"未知用户")
            self.assertEqual(issues[4].owner,"秘密名称")
            _resolve_issue_owners(issues,db,None)
            self.assertTrue(all(i.owner=="未知用户" for i in issues))

if __name__ == "__main__":
    unittest.main()
