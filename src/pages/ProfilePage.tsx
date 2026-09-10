import React, { useState } from 'react';
import {
  GraduationCap,
  Briefcase,
  FolderGit2,
  Award,
  Edit3,
  FileText,
  Clock,
  Mail,
  Phone,
  Compass,
  CheckCircle2,
  Plus,
  Trash2,
  Sparkles,
  ArrowRight,
  UploadCloud,
  ShieldAlert
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { SkillBar } from '../components/common/SkillBar';
import { Modal } from '../components/common/Modal';
import { StudentProfile, SkillCategory, CareerRole, Skill, SkillLevel } from '../types';

interface ProfilePageProps {
  student: StudentProfile;
  careers: CareerRole[];
  onUpdateProfile: (updated: Partial<StudentProfile>) => void;
  onNavigateToCareers: () => void;
  onNavigateToResume: () => void;
  onNavigateToDashboard?: () => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({
  student,
  careers,
  onUpdateProfile,
  onNavigateToCareers,
  onNavigateToResume,
  onNavigateToDashboard
}) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({
    name: student.name,
    email: student.email,
    phone: student.phone || '',
    degree: student.degree || '',
    institution: student.institution || '',
    cgpa: student.cgpa || 0,
    targetCareerId: student.targetCareerId || (careers[0]?.id || 'career_fullstack'),
    weeklyHours: student.preferences?.weeklyHours || 12,
    learningStyle: student.preferences?.learningStyle || 'video'
  });

  // Manual skill adding state
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState<SkillCategory>('Frontend');
  const [newSkillProficiency, setNewSkillProficiency] = useState(75);

  const categories: SkillCategory[] = ['Frontend', 'Backend', 'Database', 'Tools', 'Other'];
  const targetCareer = careers.find((c) => c.id === student.targetCareerId) || careers[0];
  const isPersonalized = Boolean(student.resumeFile !== null || student.skills.length > 0);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdateProfile({
      name: editFormData.name,
      email: editFormData.email,
      phone: editFormData.phone,
      degree: editFormData.degree,
      institution: editFormData.institution,
      cgpa: Number(editFormData.cgpa),
      targetCareerId: editFormData.targetCareerId,
      preferences: {
        ...student.preferences,
        weeklyHours: Number(editFormData.weeklyHours),
        learningStyle: editFormData.learningStyle as 'video' | 'reading' | 'interactive'
      }
    });
    setIsEditModalOpen(false);
  };

  const getSkillLevel = (proficiency: number): SkillLevel => {
    if (proficiency >= 85) return 'Expert';
    if (proficiency >= 70) return 'Proficient';
    if (proficiency >= 45) return 'Familiar';
    return 'Novice';
  };

  const handleAddCustomSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    const skillExists = student.skills.some(
      s => s.name.toLowerCase() === newSkillName.trim().toLowerCase()
    );

    if (skillExists) {
      alert(`Skill "${newSkillName}" is already in your profile.`);
      return;
    }

    const newSkill: Skill = {
      name: newSkillName.trim(),
      category: newSkillCategory,
      proficiency: Number(newSkillProficiency),
      level: getSkillLevel(Number(newSkillProficiency)),
      verified: true,
      detectedFrom: 'Manual self-assessment'
    };

    const updatedSkills = [...student.skills, newSkill];
    onUpdateProfile({
      skills: updatedSkills,
      targetCareerId: student.targetCareerId || targetCareer.id
    });

    setNewSkillName('');
    setNewSkillProficiency(75);
  };

  const handleQuickAddSkill = (skillName: string, category: SkillCategory, proficiency: number = 75) => {
    if (student.skills.some(s => s.name.toLowerCase() === skillName.toLowerCase())) {
      return;
    }

    const newSkill: Skill = {
      name: skillName,
      category,
      proficiency,
      level: getSkillLevel(proficiency),
      verified: true,
      detectedFrom: 'Quick profile builder'
    };

    const updatedSkills = [...student.skills, newSkill];
    onUpdateProfile({
      skills: updatedSkills,
      targetCareerId: student.targetCareerId || targetCareer.id
    });
  };

  const handleRemoveSkill = (skillName: string) => {
    const updatedSkills = student.skills.filter(s => s.name !== skillName);
    onUpdateProfile({ skills: updatedSkills });
  };

  const popularSkills: Array<{ name: string; category: SkillCategory; proficiency: number }> = [
    { name: 'JavaScript', category: 'Frontend', proficiency: 80 },
    { name: 'React', category: 'Frontend', proficiency: 75 },
    { name: 'TypeScript', category: 'Frontend', proficiency: 65 },
    { name: 'HTML/CSS', category: 'Frontend', proficiency: 85 },
    { name: 'Node.js', category: 'Backend', proficiency: 60 },
    { name: 'Express', category: 'Backend', proficiency: 60 },
    { name: 'REST APIs', category: 'Backend', proficiency: 65 },
    { name: 'Python', category: 'Backend', proficiency: 70 },
    { name: 'MongoDB', category: 'Database', proficiency: 65 },
    { name: 'SQL', category: 'Database', proficiency: 60 },
    { name: 'Git', category: 'Tools', proficiency: 75 },
    { name: 'Docker', category: 'Tools', proficiency: 50 },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Student Profile"
        subtitle="Verified academic dossier, technical competencies, and active target trajectories."
        badge="Academic Dossier"
        action={
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="px-3.5 py-1.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1.5"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Edit Profile</span>
          </button>
        }
      />

      {/* ZERO KNOWLEDGE ALERT / NOTIFICATION BANNER */}
      {!isPersonalized ? (
        <div className="p-4 bg-paper rounded-md border border-editorial-amber/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-editorial-amber shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-charcoal-900">
                Zero-Knowledge Dossier Mode
              </div>
              <p className="text-charcoal-600 mt-0.5">
                No technical skills or resume indexed yet. Use the <strong>Manual Profile Builder</strong> below to self-report your skills, or upload your resume for automatic parsing.
              </p>
            </div>
          </div>

          <button
            onClick={onNavigateToResume}
            className="shrink-0 px-3.5 py-1.5 bg-forest-800 hover:bg-forest-900 text-white font-medium rounded-sm shadow-subtle transition-colors flex items-center gap-1.5 self-start sm:self-auto"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Resume Instead</span>
          </button>
        </div>
      ) : (
        <div className="p-3 bg-forest-50 border border-forest-200 rounded-md flex items-center justify-between text-xs text-forest-900">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0" />
            <span>
              <strong>Personalized Profile Calibrated:</strong> {student.skills.length} technical skills actively benchmarked.
            </span>
          </div>
          {onNavigateToDashboard && (
            <button
              onClick={onNavigateToDashboard}
              className="font-medium text-forest-900 hover:underline flex items-center gap-1 font-mono text-[11px]"
            >
              <span>View Personalized Dashboard</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      )}

      {/* Student Overview Header Card */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-6 border-b border-paper-border">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-sm bg-forest-800 text-white font-serif font-bold text-2xl flex items-center justify-center shadow-subtle shrink-0">
              {student.name.charAt(0) || 'C'}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="font-serif text-2xl font-medium text-charcoal-900">
                  {student.name}
                </h2>
                <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
                  isPersonalized
                    ? 'bg-forest-100 text-forest-900 border-forest-200'
                    : 'bg-paper-dark text-charcoal-600 border-paper-border'
                }`}>
                  {isPersonalized ? 'Calibrated Dossier' : 'Zero-Knowledge Slate'}
                </span>
              </div>
              <p className="text-xs text-charcoal-600 mt-1 font-normal">
                {student.degree || 'Degree & major not yet specified (Click Edit Profile)'}
              </p>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-charcoal-500 font-mono">
                <span className="flex items-center gap-1">
                  <GraduationCap className="w-3.5 h-3.5 text-charcoal-400" />
                  {student.institution || 'Institution pending'} {student.graduationYear ? `(Class of ${student.graduationYear})` : ''}
                </span>
                <span>•</span>
                <span>CGPA: <strong className="text-charcoal-900">{student.cgpa ? student.cgpa : '—'}</strong> / 10.0</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:items-end gap-1.5 text-xs text-charcoal-600 font-mono">
            <span className="flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-charcoal-400" /> {student.email || 'Email not provided'}
            </span>
            {student.phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5 text-charcoal-400" /> {student.phone}
              </span>
            )}
            <span className="flex items-center gap-1.5 text-forest-800">
              <Clock className="w-3.5 h-3.5" /> {student.preferences?.weeklyHours || 10}h study target / week
            </span>
          </div>
        </div>

        {/* Bio & Current Target Role Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-1">
          <div className="lg:col-span-2 space-y-2">
            <span className="text-[10px] font-mono uppercase tracking-widest text-charcoal-400 block">
              Candidate Summary & Objective
            </span>
            <p className="text-xs text-charcoal-700 leading-relaxed font-normal">
              {student.bio ||
                'No candidate statement recorded. Click "Edit Profile" above to provide your background, coursework focus, and primary software engineering interests.'}
            </p>
          </div>

          <div className="p-4 bg-paper rounded-sm border border-paper-border space-y-2 self-start">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[10px] font-mono uppercase tracking-wider text-charcoal-500">
                Target Role
              </span>
              <button
                onClick={onNavigateToCareers}
                className="text-forest-800 hover:underline text-[11px] font-mono"
              >
                Change →
              </button>
            </div>
            <div className="font-serif text-base font-semibold text-charcoal-900">
              {targetCareer.title}
            </div>
            <p className="text-[11px] text-charcoal-600 line-clamp-2 leading-tight">
              {targetCareer.description}
            </p>
          </div>
        </div>
      </div>

      {/* INTERACTIVE MANUAL SKILL BUILDER SECTION */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-paper-border">
          <div>
            <h3 className="font-serif text-xl font-medium text-charcoal-900">
              Manual Skill Builder
            </h3>
            <p className="text-xs text-charcoal-500 mt-0.5">
              Self-report the technologies, frameworks, and tools you are familiar with to personalize your readiness benchmarks.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-forest-800 bg-forest-50 px-2.5 py-1 rounded border border-forest-200">
              {student.skills.length} Competencies Recorded
            </span>
          </div>
        </div>

        {/* 1-Click Popular Skill Tag Chips */}
        <div className="space-y-2">
          <span className="text-[11px] font-mono uppercase tracking-wider text-charcoal-500 block">
            Click to Quick-Add Common Technologies:
          </span>
          <div className="flex flex-wrap gap-2">
            {popularSkills.map((ps) => {
              const alreadyHas = student.skills.some(
                s => s.name.toLowerCase() === ps.name.toLowerCase()
              );
              return (
                <button
                  key={ps.name}
                  type="button"
                  onClick={() => handleQuickAddSkill(ps.name, ps.category, ps.proficiency)}
                  disabled={alreadyHas}
                  className={`px-3 py-1.5 text-xs font-mono rounded transition-all flex items-center gap-1.5 ${
                    alreadyHas
                      ? 'bg-forest-100 text-forest-900 border border-forest-200 opacity-60 cursor-default'
                      : 'bg-paper hover:bg-paper-dark text-charcoal-800 border border-paper-border hover:border-charcoal-400'
                  }`}
                >
                  {alreadyHas ? <CheckCircle2 className="w-3 h-3 text-forest-700" /> : <Plus className="w-3 h-3 text-charcoal-400" />}
                  <span>{ps.name}</span>
                  <span className="text-[10px] text-charcoal-400">({ps.category})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Skill Input Form */}
        <form onSubmit={handleAddCustomSkill} className="p-4 bg-paper rounded-sm border border-paper-border space-y-3">
          <div className="text-xs font-medium text-charcoal-900 flex items-center gap-1.5">
            <Plus className="w-4 h-4 text-forest-800" />
            <span>Add Custom Technical Competency</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <div className="sm:col-span-2">
              <label className="block text-charcoal-600 text-[11px] font-mono uppercase mb-1">
                Technology Name
              </label>
              <input
                type="text"
                placeholder="e.g. Next.js, Kubernetes, PostgreSQL"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                className="w-full px-3 py-1.5 bg-white border border-paper-border rounded-sm text-xs text-charcoal-900 focus:outline-none focus:border-forest-800"
              />
            </div>

            <div>
              <label className="block text-charcoal-600 text-[11px] font-mono uppercase mb-1">
                Category
              </label>
              <select
                value={newSkillCategory}
                onChange={(e) => setNewSkillCategory(e.target.value as SkillCategory)}
                className="w-full px-3 py-1.5 bg-white border border-paper-border rounded-sm text-xs text-charcoal-900 focus:outline-none focus:border-forest-800"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-charcoal-600 text-[11px] font-mono uppercase mb-1">
                Proficiency ({newSkillProficiency}%)
              </label>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={newSkillProficiency}
                onChange={(e) => setNewSkillProficiency(Number(e.target.value))}
                className="w-full accent-forest-800 cursor-pointer mt-1"
              />
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={!newSkillName.trim()}
              className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-medium rounded-sm shadow-subtle transition-colors disabled:opacity-40 flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add to Profile</span>
            </button>
          </div>
        </form>

        {/* Existing Skills Breakdown by Category */}
        <div className="pt-2 space-y-6">
          {student.skills.length === 0 ? (
            <div className="py-8 text-center border-2 border-dashed border-paper-border rounded-sm space-y-2">
              <p className="text-xs text-charcoal-500 font-mono">
                No technical skills have been added yet.
              </p>
              <p className="text-xs text-charcoal-600 max-w-sm mx-auto">
                Use the quick buttons or the form above to add your first skill and instantly calibrate your career dashboard.
              </p>
            </div>
          ) : (
            categories.map((category) => {
              const categorySkills = student.skills.filter((s) => s.category === category);
              if (categorySkills.length === 0) return null;

              return (
                <div key={category} className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase tracking-widest text-forest-800 font-semibold">
                      {category} ({categorySkills.length})
                    </span>
                    <div className="h-px bg-paper-border flex-1" />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {categorySkills.map((skill) => (
                      <div key={skill.name} className="relative group">
                        <SkillBar
                          name={skill.name}
                          percentage={skill.proficiency}
                          level={skill.level}
                          verified={skill.verified}
                        />
                        <button
                          type="button"
                          onClick={() => handleRemoveSkill(skill.name)}
                          className="absolute -top-1 -right-1 p-1 text-charcoal-400 hover:text-editorial-rust opacity-0 group-hover:opacity-100 transition-opacity bg-white border border-paper-border rounded-full shadow-subtle"
                          title="Remove skill"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Experience, Projects & Certifications Grids */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Experience Card */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-paper-border">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Experience & Internships
              </h3>
            </div>
            <span className="text-xs font-mono text-charcoal-500">
              {student.experience.length} Records
            </span>
          </div>

          <div className="space-y-3">
            {student.experience.length === 0 ? (
              <div className="py-6 text-center text-xs text-charcoal-500 font-mono">
                No internships recorded. Uploading a resume auto-fills this section.
              </div>
            ) : (
              student.experience.map((exp, idx) => (
                <div key={idx} className="p-3 bg-paper rounded-sm border border-paper-border text-xs space-y-1">
                  <div className="font-semibold text-charcoal-900">{exp.title}</div>
                  <div className="text-charcoal-500 font-mono text-[11px] flex justify-between">
                    <span>{exp.company}</span>
                    <span>{exp.period}</span>
                  </div>
                  <p className="text-charcoal-600 text-[11px] leading-relaxed pt-1">
                    {exp.description}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Projects Card */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-paper-border">
            <div className="flex items-center gap-2">
              <FolderGit2 className="w-4 h-4 text-forest-800" />
              <h3 className="font-serif text-lg font-medium text-charcoal-900">
                Technical Projects
              </h3>
            </div>
            <span className="text-xs font-mono text-charcoal-500">
              {student.projects.length} Projects
            </span>
          </div>

          <div className="space-y-3">
            {student.projects.length === 0 ? (
              <div className="py-6 text-center text-xs text-charcoal-500 font-mono">
                No projects indexed yet.
              </div>
            ) : (
              student.projects.map((proj, idx) => (
                <div key={idx} className="p-3 bg-paper rounded-sm border border-paper-border text-xs space-y-1.5">
                  <div className="font-semibold text-charcoal-900">{proj.title}</div>
                  <div className="flex flex-wrap gap-1">
                    {proj.tech.map((t) => (
                      <span
                        key={t}
                        className="px-1.5 py-0.2 text-[9px] font-mono rounded bg-white text-charcoal-700 border border-paper-border"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                  <p className="text-charcoal-600 text-[11px] leading-relaxed">
                    {proj.description}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Edit Profile Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Academic Dossier"
      >
        <form onSubmit={handleSaveProfile} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Full Name</label>
              <input
                type="text"
                value={editFormData.name}
                onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
                required
              />
            </div>
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Email</label>
              <input
                type="email"
                value={editFormData.email}
                onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Degree Program</label>
              <input
                type="text"
                placeholder="e.g. B.Tech Computer Science & Engineering"
                value={editFormData.degree}
                onChange={(e) => setEditFormData({ ...editFormData, degree: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
              />
            </div>
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Institution</label>
              <input
                type="text"
                placeholder="e.g. Apex Institute of Technology"
                value={editFormData.institution}
                onChange={(e) => setEditFormData({ ...editFormData, institution: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">CGPA (out of 10)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="10"
                value={editFormData.cgpa}
                onChange={(e) => setEditFormData({ ...editFormData, cgpa: Number(e.target.value) })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900 font-mono"
              />
            </div>
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Weekly Study Hours</label>
              <input
                type="number"
                min="2"
                max="40"
                value={editFormData.weeklyHours}
                onChange={(e) => setEditFormData({ ...editFormData, weeklyHours: Number(e.target.value) })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900 font-mono"
              />
            </div>
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Learning Style</label>
              <select
                value={editFormData.learningStyle}
                onChange={(e) => setEditFormData({ ...editFormData, learningStyle: e.target.value as 'video' | 'reading' | 'interactive' })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
              >
                <option value="video">Video & Tutorials</option>
                <option value="reading">Documentation & Books</option>
                <option value="interactive">Interactive / Coding</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-charcoal-700 font-medium mb-1">Target Career Role</label>
            <select
              value={editFormData.targetCareerId}
              onChange={(e) => setEditFormData({ ...editFormData, targetCareerId: e.target.value })}
              className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
            >
              {careers.map((career) => (
                <option key={career.id} value={career.id}>
                  {career.title} ({career.currentMatchPercentage}% Match)
                </option>
              ))}
            </select>
          </div>

          <div className="pt-4 border-t border-paper-border flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsEditModalOpen(false)}
              className="px-3 py-1.5 border border-paper-border text-charcoal-600 rounded-sm hover:bg-paper-dark"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 bg-forest-800 hover:bg-forest-900 text-white rounded-sm font-medium"
            >
              Save Changes
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
