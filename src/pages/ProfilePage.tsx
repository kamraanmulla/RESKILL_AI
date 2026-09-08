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
  CheckCircle2
} from 'lucide-react';
import { SectionHeader } from '../components/common/SectionHeader';
import { SkillBar } from '../components/common/SkillBar';
import { Modal } from '../components/common/Modal';
import { StudentProfile, SkillCategory, CareerRole } from '../types';

interface ProfilePageProps {
  student: StudentProfile;
  careers: CareerRole[];
  onUpdateProfile: (updated: Partial<StudentProfile>) => void;
  onNavigateToCareers: () => void;
  onNavigateToResume: () => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({
  student,
  careers,
  onUpdateProfile,
  onNavigateToCareers,
  onNavigateToResume
}) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({
    name: student.name,
    email: student.email,
    phone: student.phone,
    degree: student.degree,
    institution: student.institution,
    cgpa: student.cgpa,
    targetCareerId: student.targetCareerId,
    weeklyHours: student.preferences.weeklyHours,
    learningStyle: student.preferences.learningStyle
  });

  const categories: SkillCategory[] = ['Frontend', 'Backend', 'Database', 'Tools', 'Other'];

  const targetCareer = careers.find((c) => c.id === student.targetCareerId) || careers[0];

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

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <SectionHeader
        title="Student Profile"
        subtitle="Verified academic background, technical skills, and career trajectories."
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

      {/* Student Overview Header Card */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-6 border-b border-paper-border">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-sm bg-forest-800 text-white font-serif font-bold text-2xl flex items-center justify-center shadow-subtle shrink-0">
              {student.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="font-serif text-2xl font-medium text-charcoal-900">
                  {student.name}
                </h2>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-forest-100 text-forest-900 border border-forest-200">
                  Active Student
                </span>
              </div>
              <p className="text-xs text-charcoal-600 mt-1 font-normal">
                {student.degree}
              </p>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-charcoal-500 font-mono">
                <span className="flex items-center gap-1">
                  <GraduationCap className="w-3.5 h-3.5 text-charcoal-400" />
                  {student.institution} (Class of {student.graduationYear})
                </span>
                <span>•</span>
                <span>CGPA: <strong className="text-charcoal-900">{student.cgpa}</strong> / 10.0</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:items-end gap-1.5 text-xs text-charcoal-600 font-mono">
            <span className="flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-charcoal-400" /> {student.email}
            </span>
            <span className="flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-charcoal-400" /> {student.phone}
            </span>
          </div>
        </div>

        {/* Bio */}
        <p className="text-xs text-charcoal-600 leading-relaxed max-w-3xl">
          {student.bio}
        </p>

        {/* Status Strip: Target Career, Resume, Preferences */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          {/* Target Career Tile */}
          <div className="p-3.5 bg-paper rounded-sm border border-paper-border flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase font-mono tracking-wider text-charcoal-500">
                Target Trajectory
              </div>
              <div className="text-xs font-semibold text-charcoal-900 mt-0.5">
                {targetCareer.title}
              </div>
            </div>
            <button
              onClick={onNavigateToCareers}
              className="p-1.5 text-charcoal-500 hover:text-forest-800 rounded hover:bg-paper-dark transition-colors"
              title="Change target career"
            >
              <Compass className="w-4 h-4" />
            </button>
          </div>

          {/* Uploaded Resume Tile */}
          <div className="p-3.5 bg-paper rounded-sm border border-paper-border flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase font-mono tracking-wider text-charcoal-500">
                Primary Resume
              </div>
              <div className="text-xs font-semibold text-charcoal-900 truncate max-w-[150px] mt-0.5">
                {student.resumeFile?.name || 'No resume file'}
              </div>
            </div>
            <button
              onClick={onNavigateToResume}
              className="p-1.5 text-charcoal-500 hover:text-forest-800 rounded hover:bg-paper-dark transition-colors"
              title="View or re-upload resume"
            >
              <FileText className="w-4 h-4" />
            </button>
          </div>

          {/* Learning Cadence */}
          <div className="p-3.5 bg-paper rounded-sm border border-paper-border flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase font-mono tracking-wider text-charcoal-500">
                Weekly Cadence
              </div>
              <div className="text-xs font-semibold text-charcoal-900 mt-0.5">
                {student.preferences.weeklyHours} hours/week • {student.preferences.learningStyle}
              </div>
            </div>
            <Clock className="w-4 h-4 text-charcoal-400" />
          </div>
        </div>
      </div>

      {/* Categorized Skills Matrix */}
      <div className="bg-white border border-paper-border rounded-md p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-paper-border">
          <div>
            <h3 className="font-serif text-xl font-medium text-charcoal-900">
              Categorized Skill Inventory
            </h3>
            <p className="text-xs text-charcoal-500">
              Extracted from verified college coursework, GitHub repositories, and internship logs.
            </p>
          </div>
          <span className="text-xs font-mono text-charcoal-500">
            {student.skills.length} Total Skills
          </span>
        </div>

        <div className="space-y-6">
          {categories.map((category) => {
            const categorySkills = student.skills.filter((s) => s.category === category);
            if (categorySkills.length === 0) return null;

            return (
              <div key={category} className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono uppercase tracking-widest text-forest-800 font-semibold">
                    {category}
                  </span>
                  <div className="h-px bg-paper-border flex-1" />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {categorySkills.map((skill) => (
                    <SkillBar
                      key={skill.name}
                      name={skill.name}
                      percentage={skill.proficiency}
                      level={skill.level}
                      verified={skill.verified}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Experience, Projects & Certifications Grids */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Experience Card */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-paper-border">
            <Briefcase className="w-4 h-4 text-forest-800" />
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Experience & Internships
            </h3>
          </div>

          <div className="space-y-4">
            {student.experience.map((exp, idx) => (
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
            ))}
          </div>
        </div>

        {/* Projects Card */}
        <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-paper-border">
            <FolderGit2 className="w-4 h-4 text-forest-800" />
            <h3 className="font-serif text-lg font-medium text-charcoal-900">
              Technical Projects
            </h3>
          </div>

          <div className="space-y-4">
            {student.projects.map((proj, idx) => (
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
            ))}
          </div>
        </div>
      </div>

      {/* Certifications Card */}
      <div className="bg-white border border-paper-border rounded-md p-6 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-paper-border">
          <Award className="w-4 h-4 text-forest-800" />
          <h3 className="font-serif text-lg font-medium text-charcoal-900">
            Licenses & Certifications
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {student.certifications.map((cert, idx) => (
            <div key={idx} className="p-3 bg-paper rounded-sm border border-paper-border text-xs space-y-1">
              <div className="font-semibold text-charcoal-900 flex items-center justify-between">
                <span>{cert.title}</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-forest-700" />
              </div>
              <div className="text-[11px] font-mono text-charcoal-500">
                {cert.issuer} • Issued {cert.year}
              </div>
              {cert.credentialId && (
                <div className="text-[10px] font-mono text-charcoal-400">
                  ID: {cert.credentialId}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Edit Profile Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Student Profile"
        subtitle="Update your academic credentials, target career, and weekly learning availability."
        maxWidth="lg"
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
                value={editFormData.degree}
                onChange={(e) => setEditFormData({ ...editFormData, degree: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
                required
              />
            </div>
            <div>
              <label className="block text-charcoal-700 font-medium mb-1">Institution</label>
              <input
                type="text"
                value={editFormData.institution}
                onChange={(e) => setEditFormData({ ...editFormData, institution: e.target.value })}
                className="w-full px-3 py-1.5 border border-paper-border rounded-sm bg-paper focus:bg-white text-charcoal-900"
                required
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
                required
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
                required
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
