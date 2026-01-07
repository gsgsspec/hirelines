from datetime import datetime

from app_api.functions.services import getProfileDetailsService

RULES = {
    # "education": {
    #     "set_1": {
    #         "items": [
    #             "B-Tech",
    #             "Bachelor of Technology"
    #             "Btech",
    #             "BE",
    #             "BSc",
    #             "BCom",
    #             "BA",
    #             "BBA",
    #             "BBM",
    #             "BCA",
    #             "BHM",
    #             "BDes",
    #             "BFA",
    #             "BS",
    #         ],
    #         "points": 6,
    #     },
    #     "set_2": {
    #         "items": [
    #             "MBA",
    #             "Master of business applications",
    #             "MCA",
    #             "Master of computer applications",
    #             "MTech",
    #             "Master of Technology",
    #             "M-Tech",
    #             "ME",
    #             "MS",
    #             "MA",
    #             "MCom",
    #             "MSc",
    #             "M.Sc",
    #             "MPhil",
    #             "LLM",
    #             "MPH",
    #             "MDes",
    #             "MFA",
    #             "MEd",
    #             "PGDM",
    #             "PGDBM",
    #         ],
    #         "points": 10,
    #     },
    #     "max_points": 10,
    # },
    "education": {
        "set_1": {
            "items": ["B"],
            "points": 6,
        },
        "set_2": {
            "items": ["P","M"],
            "points": 10,
        },
        "max_points": 10,
    },
    "experience": {
        "sets": [
            {"min": 3, "max": 5, "base_points": 10},
        ],
        "deduction": {"per_item": 1, "min_score": 0},
    },
    "projects": {
        "base_points": 10,
        "min_required": 3,
        "deduction": {"per_short_project": 1, "min_score": 0},
    },
    # "certificates": {"points_per_item": 1, "max_points": 5},
    # "awards": {"points_per_item": 1, "max_points": 5},
    "skills": {
        "tier_1": {
            "skills": [
                "python",
                "java",
                "c",
                "c++",
                "c#",
                "go",
                "rust",
                "scala",
                "kotlin",
                "swift",
                "mysql",
                "postgresql",
                "oracle",
                "mongodb",
                "redis",
                "sqlite",
                "bash",
                "powershell",
                "aws",
                "azure",
                "gcp",
            ],
            "points_per_skill": 10,
            "max_points": 20,
        },
        "tier_2": {
            "skills": [
                "react",
                "angular",
                "vue",
                "svelte",
                "nodejs",
                "express",
                "nestjs",
                "django",
                "flask",
                "fastapi",
                "spring",
                "spring boot",
                "laravel",
                "dotnet",
                "nextjs",
                "nuxtjs",
                "graphql",
                "rest api",
                "docker",
                "kubernetes",
                "jenkins",
                "gitlab ci",
                "github actions",
            ],
            "points_per_skill": 5,
            "max_points": 20,
        },
        "tier_3": {
            "skills": [
                "html",
                "css",
                "javascript",
                "typescript",
                "jquery",
                "bootstrap",
                "tailwind",
                "material ui",
                "chakra ui",
                "sass",
                "less",
                "webpack",
                "vite",
                "babel",
                "npm",
                "yarn",
                "pnpm",
                "eslint",
                "prettier",
                "git",
                "github",
                "bitbucket",
                "json",
                "xml",
                "responsive design",
                "cross browser testing",
            ],
            "points_per_skill": 2.5,
            "max_points": 20,
        },
    },
}


class CalculateProfileScoring:
    
    def __init__(self):
        self.rules = RULES
        self.current_year = datetime.now().year
        self.SECTION_MAX = {
            "education": 10,
            "experience": 10,
            "projects": 10,
            "certificates": 5,
            "awards": 5,
            "skills": 60,
        }

        # Normalize education items to lowercase
        for rule in self.rules["education"].values():
            if isinstance(rule, dict) and "items" in rule:
                rule["items"] = {item.lower() for item in rule["items"]}

        # Skills already case-insensitive
        for tier in self.rules["skills"].values():
            tier["skills"] = {s.lower() for s in tier["skills"]}

    # ---------- HELPERS ----------

    def _normalize_text(self, text: str) -> str:
        """Normalize text for case-insensitive + substring match"""
        return (
            text.lower()
            .replace(".", "")
            .replace("-", "")
            .strip()
        )

    def calculate_experience_years(self, experience):
        years = 0
        for job in experience:
            if not isinstance(job, dict):
                continue
            start = job.get("yearfrom")
            end = job.get("yearto") or self.current_year
            if start and end:
                years += max(0, end - start)
        return years

    def apply_deduction(self, base_score, item_count, rule):
        deduction = item_count * rule.get("per_item", 0)
        return max(rule.get("min_score", 0), base_score - deduction)

    def calculate_capped_item_score(self, items, points_per_item, max_points):
        if not isinstance(items, list):
            return 0
        return min(len(items) * points_per_item, max_points)

    # ---------- SCORERS ----------

    # def score_education(self, profile):
    #     education = profile.get("education", [])
    #     if not isinstance(education, list):
    #         return 0

    #     # Case-insensitive matching
    #     courses = {
    #         e.get("course").lower()
    #         for e in education
    #         if isinstance(e, dict) and isinstance(e.get("course"), str)
    #     }

    #     score = 0

    #     for key, rule in self.rules["education"].items():
    #         if key == "max_points":
    #             continue

    #         rule_items = {item.lower() for item in rule["items"]}
    #         if courses & rule_items:
    #             score += rule["points"]

    #     #  CAP education score
    #     max_points = self.rules["education"].get("max_points", score)
    #     return min(score, max_points)

    def score_education(self, profile):
        education = profile.get("education", [])
        if not isinstance(education, list):
            return 0

        score = 0

        for edu in education:
            if not isinstance(edu, dict):
                continue

            course = edu.get("course")
            if not isinstance(course, str) or not course.strip():
                continue

            #  Case-insensitive: normalize course
            course_start = course.strip()[0].upper()

            for rule in self.rules["education"].values():
                if not isinstance(rule, dict) or "items" not in rule:
                    continue

                #  Case-insensitive: normalize rule items
                rule_items = {item.upper() for item in rule["items"]}

                if course_start in rule_items:
                    score += rule["points"]

        # Apply max cap
        max_points = self.rules["education"].get("max_points", score)
        return min(score, max_points)

    def score_experience(self, profile):
        experience = profile.get("experience", [])

        if not isinstance(experience, list) or len(experience) == 0:
            return 0

        base_points = self.rules["experience"]["sets"][0]["base_points"]
        min_required = self.rules["experience"]["sets"][0]["min"]

        company_years = []
        total_years = 0

        for job in experience:
            if not isinstance(job, dict):
                continue

            start = job.get("yearfrom")
            end = job.get("yearto") or self.current_year

            if isinstance(start, int) and isinstance(end, int) and end > start:
                years = end - start
                company_years.append(years)
                total_years += years

        if total_years == 0:
            return 0

        score = base_points

        if total_years < min_required:
            score -= min_required - total_years

        for yrs in company_years:
            if yrs < min_required:
                score -= 1

        return max(0, score)

    def score_projects(self, profile):
        projects = profile.get("projects", [])

        if not isinstance(projects, list) or len(projects) == 0:
            return 0

        rules = self.rules["projects"]
        base_points = rules["base_points"]
        min_required = rules["min_required"]
        per_short_project = rules["deduction"]["per_short_project"]
        min_score = rules["deduction"]["min_score"]

        score = base_points
        valid_project_found = False

        for project in projects:
            if not isinstance(project, dict):
                continue

            start = project.get("yearsfrom")
            end = project.get("yearsto") or self.current_year

            if isinstance(start, int) and isinstance(end, int) and end > start:
                valid_project_found = True
                years = end - start

                if years < min_required:
                    score -= per_short_project

        if not valid_project_found:
            return 0

        return max(min_score, score)

    # def score_certificates(self, profile):
    #     return self.calculate_capped_item_score(
    #         profile.get("certificates", []),
    #         self.rules["certificates"]["points_per_item"],
    #         self.rules["certificates"]["max_points"],
    #     )
    def score_certificates(self, profile):
        certificates = profile.get("certificates", [])
        print("certificates",certificates)
        experience = profile.get("experience", [])
        print("experience",experience)

       

        cert_count = len(certificates)
        print("cert_count",cert_count)
        exp_years = self.calculate_experience_years(experience)
        print("exp_years",exp_years)

        if not isinstance(certificates, list) or len(certificates) == 0:
            return 0

       
        if exp_years <= 2:
            expected = 1
        elif exp_years <= 4:
            expected = 2
        elif exp_years <= 6:
            expected = 3
        elif exp_years <= 8:
            expected = 4
        else:
            expected = 5

        
        if cert_count >= expected:
            return 5

        
        missing = expected - cert_count
        score = 5 - missing

        return max(0, score)
    
    def score_awards(self, profile):
        awards = profile.get("awards", [])
        print("awards",awards)
        experience = profile.get("experience", [])
        print("experience",experience)

        award_count = len(awards)
        print("award_count",award_count)
        exp_years = self.calculate_experience_years(experience)
        print("exp_years",exp_years)

        
        if award_count == 0:
            return 0

       
        if exp_years <= 2:
            expected = 1
        elif exp_years <= 4:
            expected = 2
        elif exp_years <= 6:
            expected = 3
        elif exp_years <= 8:
            expected = 4
        else:
            expected = 5

        
        if award_count >= expected:
            return 5

        
        score = 5 - (expected - award_count)

        return max(0, score)


    # def score_awards(self, profile):
    #     return self.calculate_capped_item_score(
    #         profile.get("awards", []),
    #         self.rules["awards"]["points_per_item"],
    #         self.rules["awards"]["max_points"],
    #     )

    def score_skills(self, profile):
        primary = profile.get("skills", {}).get("primaryskills") or ""
        secondary = profile.get("skills", {}).get("secondaryskills") or ""

        skills_text = f"{primary},{secondary}".lower()
        remaining_skills = {s.strip() for s in skills_text.split(",") if s.strip()}

        score = 0

        for tier_key in ["tier_1", "tier_2", "tier_3"]:
            tier = self.rules["skills"][tier_key]
            matched = remaining_skills & tier["skills"]

            score += min(
                len(matched) * tier["points_per_skill"],
                tier["max_points"],
            )

            remaining_skills -= matched
            if not remaining_skills:
                break

        return score

    # ---------- MAIN ENTRY ----------

    def score_profile(self, profile_id):
        from app_api.functions.services import getProfileDetailsService
        
        profile = getProfileDetailsService(profile_id)

        raw_scores = {
            "education": self.score_education(profile),
            "experience": self.score_experience(profile),
            "projects": self.score_projects(profile),
            "certificates": self.score_certificates(profile),
            "awards": self.score_awards(profile),
            "skills": self.score_skills(profile),
        }
        print("raw_scores",raw_scores)
        breakdown = {}
        total_score = 0

        for section, score in raw_scores.items():
            max_points = self.SECTION_MAX[section]

            pct = (score / max_points) * 100 if max_points else 0

            # precision control
            pct = int(pct * 10) / 10
            pct = int(pct) if isinstance(pct, float) and pct.is_integer() else pct

            breakdown[section] = {
                "score": score,
                "percentage": pct
            }

            total_score += score

        overall_pct = int(total_score) if isinstance(total_score, float) and total_score.is_integer() else total_score
        print("overall_pct",overall_pct)
 
        # total_score = sum(breakdown.values())

        # percentage = (
        #     int(total_score)
        #     if isinstance(total_score, float) and total_score.is_integer()
        #     else total_score
        # )

        return {
            "total_score": total_score,
            "percentage": overall_pct,
            "breakdown": breakdown,
        }
