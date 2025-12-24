import re
from datetime import datetime
from app_api.models import JobDesc, Profile, ProfileExperience, ProfileSkills



def calculateJDProfileMatching(jobid, profiles):
    try:
        job_desc = JobDesc.objects.get(id=jobid)

        jd_min = job_desc.expmin
        jd_max = job_desc.expmax

        # print("jd_min",jd_min)
        # print("jd_max",jd_max)

        results = []

        for profile in profiles:
            profile_exp = calculate_total_experience(profile.id)
            exp_strength = calculate_experience_strength(profile_exp, jd_min)

            skill_strength = calculate_skill_strength(job_desc.skillset, profile.id)

            # print("profile_exp",profile_exp)
            # print("exp_strength",exp_strength)
            # print("skill_strength",skill_strength)

            results.append({
                "profile_id": profile.id,
                "total_experience": profile_exp,
                "exp_strength": exp_strength,
                "skill_strength": skill_strength,
            })

        return results

    except Exception as e:
        print(str(e))
        raise



def calculate_total_experience(profile_id):
    experiences = ProfileExperience.objects.filter(profileid=profile_id)

    total_years = 0
    current_year = datetime.now().year

    for exp in experiences:
        if exp.yearfrom:
            end_year = exp.yearto if exp.yearto else current_year
            total_years += max(0, end_year - exp.yearfrom)

    return total_years


def calculate_experience_strength(profile_exp, jd_min):
    if jd_min <= 0:
        return 100  # safety fallback

    if profile_exp >= jd_min:
        return 100

    strength = (profile_exp / jd_min) * 100
    return round(strength, 2)


def calculate_skill_strength(jd_skillset, profile_id):
    if not jd_skillset:
        return 100

    # ---- Fetch profile skills ----
    profile_skill_obj = (
        ProfileSkills.objects
        .filter(profileid=profile_id)
        .only("primaryskills")
        .first()
    )

    profile_primaryskills = (
        profile_skill_obj.primaryskills if profile_skill_obj else ""
    )

    # ---- Extract JD skills from dirty VARCHAR ----
    jd_skills = set()

    # Extract only words (letters, numbers)
    for word in re.findall(r"[a-zA-Z0-9]+", jd_skillset.lower()):
        # Ignore junk tokens
        if len(word) > 1:
            jd_skills.add(word)

    if not jd_skills:
        return 0

    # ---- Profile skills ----
    profile_skills = set()
    if profile_primaryskills:
        for skill in profile_primaryskills.split(","):
            profile_skills.add(skill.strip().lower())

    # ---- Matching ----
    matched = jd_skills & profile_skills
    strength = (len(matched) / len(jd_skills)) * 100

    print("jd_skills", jd_skills)
    print("profile_skills", profile_skills)
    print("matched", matched)

    return round(strength, 2)
