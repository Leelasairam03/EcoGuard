from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from datetime import datetime

class RewardType:
    """Types of rewards available."""
    BADGE = "badge"
    ACHIEVEMENT = "achievement"
    TITLE = "title"
    SPECIAL_ACCESS = "special_access"

class Badge:
    """Model for badges/achievements."""
    
    def __init__(self, badge_id: str, name: str, description: str, icon: str, 
                 points_required: int, category: str):
        self.badge_id = badge_id
        self.name = name
        self.description = description
        self.icon = icon
        self.points_required = points_required
        self.category = category
        self.rarity = self._calculate_rarity(points_required)
    
    def _calculate_rarity(self, points: int) -> str:
        """Calculate badge rarity based on points required."""
        if points <= 50:
            return "common"
        elif points <= 150:
            return "uncommon"
        elif points <= 300:
            return "rare"
        elif points <= 500:
            return "epic"
        else:
            return "legendary"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "badge_id": self.badge_id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "points_required": self.points_required,
            "category": self.category,
            "rarity": self.rarity
        }

class UserRewards:
    """Model for user rewards and achievements."""
    
    def __init__(self, email: str):
        self.email = email
        self.badges = []
        self.total_points = 0
        self.reporter_points = 0
        self.cleanup_points = 0
        self.level = 1
        self.title = "Beach Guardian"
        self.achievements = []
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "email": self.email,
            "badges": self.badges,
            "total_points": self.total_points,
            "reporter_points": self.reporter_points,
            "cleanup_points": self.cleanup_points,
            "level": self.level,
            "title": self.title,
            "achievements": self.achievements,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserRewards':
        """Create instance from dictionary."""
        instance = cls(data["email"])
        instance.badges = data.get("badges", [])
        instance.total_points = data.get("total_points", 0)
        instance.reporter_points = data.get("reporter_points", 0)
        instance.cleanup_points = data.get("cleanup_points", 0)
        instance.level = data.get("level", 1)
        instance.title = data.get("title", "Beach Guardian")
        instance.achievements = data.get("achievements", [])
        instance.created_at = data.get("created_at")
        instance.last_updated = data.get("last_updated")
        return instance

class RewardsManager:
    """Manager for the rewards system."""
    
    def __init__(self, rewards_file: Path, badges_file: Path):
        self.rewards_file = rewards_file
        self.badges_file = badges_file
        self._ensure_files_exist()
        self._initialize_default_badges()
    
    def _ensure_files_exist(self):
        """Ensure JSON files exist."""
        self.rewards_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.rewards_file.exists():
            with open(self.rewards_file, "w") as f:
                json.dump([], f, indent=2)
        
        if not self.badges_file.exists():
            with open(self.badges_file, "w") as f:
                json.dump([], f, indent=2)
    
    def _initialize_default_badges(self):
        """Initialize default badges if none exist."""
        badges = self.load_badges()
        if not badges:
            default_badges = [
                Badge("first_report", "First Report", "Submitted your first pollution report", "📝", 10, "reporter"),
                Badge("reporter_10", "Dedicated Reporter", "Submitted 10 pollution reports", "📊", 50, "reporter"),
                Badge("reporter_50", "Expert Reporter", "Submitted 50 pollution reports", "🏆", 150, "reporter"),
                Badge("first_cleanup", "First Cleanup", "Completed your first cleanup task", "🧹", 25, "cleanup"),
                Badge("cleanup_10", "Cleanup Veteran", "Completed 10 cleanup tasks", "🌟", 100, "cleanup"),
                Badge("cleanup_50", "Cleanup Master", "Completed 50 cleanup tasks", "👑", 300, "cleanup"),
                Badge("high_severity", "Crisis Responder", "Reported high-severity pollution", "🚨", 75, "reporter"),
                Badge("team_leader", "Team Leader", "Led a cleanup team", "👥", 50, "cleanup"),
                Badge("verification", "Verification Expert", "Verified 5 cleanup tasks", "✅", 100, "cleanup"),
                Badge("environmentalist", "Environmentalist", "Earned 500 total points", "🌍", 500, "general")
            ]
            
            badges = [badge.to_dict() for badge in default_badges]
            self.save_badges(badges)
    
    def load_rewards(self) -> List[Dict]:
        """Load all user rewards."""
        try:
            with open(self.rewards_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_rewards(self, rewards: List[Dict]):
        """Save user rewards."""
        with open(self.rewards_file, "w") as f:
            json.dump(rewards, f, indent=2)
    
    def load_badges(self) -> List[Dict]:
        """Load all available badges."""
        try:
            with open(self.badges_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_badges(self, badges: List[Dict]):
        """Save badges."""
        with open(self.badges_file, "w") as f:
            json.dump(badges, f, indent=2)
    
    def get_or_create_user(self, email: str) -> UserRewards:
        """Get existing user rewards or create new one."""
        rewards = self.load_rewards()
        user = next((r for r in rewards if r["email"] == email), None)
        
        if not user:
            user = UserRewards(email)
            rewards.append(user.to_dict())
            self.save_rewards(rewards)
            return user
        
        return UserRewards.from_dict(user)
    
    def award_points(self, email: str, points: int, category: str = "general"):
        """Award points to a user."""
        rewards = self.load_rewards()
        user_data = next((r for r in rewards if r["email"] == email), None)
        
        if not user_data:
            user = UserRewards(email)
        else:
            user = UserRewards.from_dict(user_data)
        
        user.total_points += points
        if category == "reporter":
            user.reporter_points += points
        elif category == "cleanup":
            user.cleanup_points += points
        
        # Update level
        user.level = (user.total_points // 100) + 1
        
        # Update title based on level
        user.title = self._get_title_for_level(user.level)
        
        user.last_updated = datetime.now().isoformat()
        
        # Check for new badges
        new_badges = self._check_for_new_badges(user)
        if new_badges:
            user.badges.extend(new_badges)
            user.achievements.append({
                "type": "badge_earned",
                "badges": new_badges,
                "date": datetime.now().isoformat()
            })
        
        # Update or add user
        if user_data:
            user_data.update(user.to_dict())
        else:
            rewards.append(user.to_dict())
        
        self.save_rewards(rewards)
        return user
    
    def _get_title_for_level(self, level: int) -> str:
        """Get title based on user level."""
        titles = {
            1: "Beach Guardian",
            2: "Coastal Protector",
            3: "Ocean Defender",
            4: "Marine Conservationist",
            5: "Environmental Champion",
            6: "Eco Warrior",
            7: "Nature Guardian",
            8: "Planet Protector",
            9: "Earth Defender",
            10: "Legendary Guardian"
        }
        return titles.get(level, "Legendary Guardian")
    
    def _check_for_new_badges(self, user: UserRewards) -> List[str]:
        """Check if user qualifies for new badges."""
        badges = self.load_badges()
        new_badges = []
        
        for badge in badges:
            if badge["badge_id"] not in user.badges:
                if self._qualifies_for_badge(user, badge):
                    new_badges.append(badge["badge_id"])
        
        return new_badges
    
    def _qualifies_for_badge(self, user: UserRewards, badge: Dict) -> bool:
        """Check if user qualifies for a specific badge."""
        badge_id = badge["badge_id"]
        
        if badge_id == "first_report" and user.reporter_points >= 10:
            return True
        elif badge_id == "reporter_10" and user.reporter_points >= 50:
            return True
        elif badge_id == "reporter_50" and user.reporter_points >= 150:
            return True
        elif badge_id == "first_cleanup" and user.cleanup_points >= 25:
            return True
        elif badge_id == "cleanup_10" and user.cleanup_points >= 100:
            return True
        elif badge_id == "cleanup_50" and user.cleanup_points >= 300:
            return True
        elif badge_id == "environmentalist" and user.total_points >= 500:
            return True
        
        return False
    
    def get_user_stats(self, email: str) -> Dict:
        """Get comprehensive user statistics."""
        user = self.get_or_create_user(email)
        badges = self.load_badges()
        
        user_badges = [b for b in badges if b["badge_id"] in user.badges]
        
        return {
            "email": user.email,
            "total_points": user.total_points,
            "reporter_points": user.reporter_points,
            "cleanup_points": user.cleanup_points,
            "level": user.level,
            "title": user.title,
            "badges": user_badges,
            "achievements": user.achievements,
            "next_level_points": (user.level * 100) - user.total_points,
            "progress_to_next": (user.total_points % 100) / 100
        }
