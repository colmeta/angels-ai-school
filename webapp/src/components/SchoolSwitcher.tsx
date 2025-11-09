/**
 * School Switcher Component
 * Allows users to switch between schools or view combined data
 */
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';

interface School {
  school_id: string;
  school_name: string;
  brand_name: string;
  primary_color: string;
  role: string;
  is_active: boolean;
  children?: any[];
  children_count: number;
}

interface SchoolSwitcherProps {
  userId: string;
  currentSchoolId?: string;
  onSchoolChange?: (schoolId: string, isAll: boolean) => void;
}

export function SchoolSwitcher({ userId, currentSchoolId, onSchoolChange }: SchoolSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedSchool, setSelectedSchool] = useState<string>(currentSchoolId || 'all');
  const queryClient = useQueryClient();

  // Fetch user's schools
  const { data: schoolsData, isLoading } = useQuery({
    queryKey: ['user-schools', userId],
    queryFn: async () => {
      const response = await apiClient.get(`/multi-school/user/${userId}/schools`);
      return response.data;
    },
  });

  // Switch school mutation
  const switchSchoolMutation = useMutation({
    mutationFn: async (schoolId: string) => {
      const response = await apiClient.post(`/multi-school/user/${userId}/switch-school`, {
        school_id: schoolId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-schools', userId] });
      queryClient.invalidateQueries({ queryKey: ['parent-dashboard'] });
    },
  });

  const handleSchoolSelect = (schoolId: string) => {
    const isAll = schoolId === 'all';
    setSelectedSchool(schoolId);
    setIsOpen(false);

    if (!isAll) {
      switchSchoolMutation.mutate(schoolId);
    }

    onSchoolChange?.(schoolId, isAll);
  };

  const schools: School[] = schoolsData?.schools || [];
  const totalSchools = schools.length;

  // Auto-select first school if none selected
  useEffect(() => {
    if (!selectedSchool && schools.length > 0) {
      setSelectedSchool(schools[0].school_id);
    }
  }, [schools, selectedSchool]);

  const currentSchool = schools.find((s) => s.school_id === selectedSchool);

  if (isLoading) {
    return (
      <div className="animate-pulse bg-gray-200 h-12 rounded-lg w-64"></div>
    );
  }

  if (totalSchools === 0) {
    return null; // No schools to switch between
  }

  if (totalSchools === 1) {
    // Only one school, show simple badge
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
        <span className="text-sm font-medium text-blue-900">
          {schools[0].brand_name || schools[0].school_name}
        </span>
      </div>
    );
  }

  // Multiple schools - show switcher
  return (
    <div className="relative">
      {/* Current School Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between gap-3 px-4 py-3 bg-white border-2 border-gray-200 rounded-lg shadow-sm hover:border-blue-400 transition-colors min-w-[280px]"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-3 h-3 rounded-full"
            style={{
              backgroundColor: currentSchool?.primary_color || '#3b82f6',
            }}
          ></div>
          <div className="text-left">
            <div className="text-sm font-semibold text-gray-900">
              {selectedSchool === 'all' ? (
                <span className="flex items-center gap-1">
                  📊 All Schools
                  <span className="text-xs font-normal text-gray-500">
                    ({totalSchools} schools)
                  </span>
                </span>
              ) : (
                currentSchool?.brand_name || currentSchool?.school_name || 'Select School'
              )}
            </div>
            {selectedSchool !== 'all' && currentSchool && (
              <div className="text-xs text-gray-500">
                {currentSchool.children_count} {currentSchool.children_count === 1 ? 'child' : 'children'}
              </div>
            )}
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          ></div>

          {/* Menu */}
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
            {/* Combined View Option */}
            <button
              onClick={() => handleSchoolSelect('all')}
              className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b ${
                selectedSchool === 'all' ? 'bg-blue-50' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">
                    📊 View All Schools
                  </div>
                  <div className="text-xs text-gray-500">
                    Combined dashboard with all children
                  </div>
                </div>
                {selectedSchool === 'all' && (
                  <svg className="w-5 h-5 text-blue-600 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </button>

            {/* Individual Schools */}
            {schools.map((school) => (
              <button
                key={school.school_id}
                onClick={() => handleSchoolSelect(school.school_id)}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                  selectedSchool === school.school_id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: school.primary_color }}
                  ></div>
                  <div>
                    <div className="text-sm font-semibold text-gray-900">
                      {school.brand_name || school.school_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {school.children_count} {school.children_count === 1 ? 'child' : 'children'} · {school.role}
                    </div>
                  </div>
                  {selectedSchool === school.school_id && (
                    <svg className="w-5 h-5 text-blue-600 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            ))}

            {/* Add School Button */}
            <button
              onClick={() => {
                setIsOpen(false);
                // TODO: Open add school dialog
                alert('Add school functionality - Coming soon!');
              }}
              className="w-full px-4 py-3 text-left border-t hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3 text-blue-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <div className="text-sm font-medium">Add Another School</div>
              </div>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
