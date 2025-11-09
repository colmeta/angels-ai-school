/**
 * Enhanced Parent Portal with Multi-School Support
 * Shows combined view or individual school view
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { SchoolSwitcher } from '@/components/SchoolSwitcher';

interface ParentPortalMultiSchoolProps {
  userId: string;
}

export function ParentPortalMultiSchool({ userId }: ParentPortalMultiSchoolProps) {
  const [selectedSchool, setSelectedSchool] = useState<string>('all');
  const [isAllSchools, setIsAllSchools] = useState(true);

  // Fetch combined dashboard for all schools
  const { data: combinedData, isPending: loadingCombined } = useQuery({
    queryKey: ['combined-dashboard', userId],
    queryFn: async () => {
      const response = await apiClient.get(`/multi-school/user/${userId}/dashboard/combined`);
      return response.data;
    },
    enabled: isAllSchools,
  });

  // Fetch single school dashboard
  const { data: singleSchoolData, isPending: loadingSingle } = useQuery({
    queryKey: ['single-school-dashboard', userId, selectedSchool],
    queryFn: async () => {
      const response = await apiClient.get(`/${selectedSchool}/parent/${userId}/dashboard`);
      return response.data;
    },
    enabled: !isAllSchools && selectedSchool !== 'all',
  });

  const handleSchoolChange = (schoolId: string, isAll: boolean) => {
    setSelectedSchool(schoolId);
    setIsAllSchools(isAll);
  };

  const isLoading = isAllSchools ? loadingCombined : loadingSingle;

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header with School Switcher */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Parent Portal</h1>
            <p className="text-gray-600 mt-1">View your children's progress and school updates</p>
          </div>
          
          <SchoolSwitcher
            userId={userId}
            currentSchoolId={selectedSchool}
            onSchoolChange={handleSchoolChange}
          />
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : isAllSchools ? (
          <CombinedDashboard data={combinedData} />
        ) : (
          <SingleSchoolDashboard data={singleSchoolData} schoolId={selectedSchool} />
        )}
      </div>
    </div>
  );
}

function CombinedDashboard({ data }: { data: any }) {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Schools</div>
          <div className="text-3xl font-bold text-gray-900">{data.total_schools}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Children</div>
          <div className="text-3xl font-bold text-gray-900">
            {data.schools.reduce((sum: number, school: any) => sum + school.children.length, 0)}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Fees Due</div>
          <div className="text-3xl font-bold text-red-600">
            {(data.total_fee_balance || 0).toLocaleString()} UGX
          </div>
        </div>
      </div>

      {/* Schools and Children */}
      {data.schools.map((school: any) => (
        <div key={school.school_id} className="bg-white rounded-lg shadow overflow-hidden">
          {/* School Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <h2 className="text-xl font-bold text-white">
              🏫 {school.brand_name || school.school_name}
            </h2>
          </div>

          {/* Children Grid */}
          <div className="p-6">
            {school.children.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No children at this school</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {school.children.map((child: any) => (
                  <div key={child.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-lg">
                        {child.first_name[0]}{child.last_name[0]}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">
                          {child.first_name} {child.last_name}
                        </div>
                        <div className="text-sm text-gray-600">{child.class_name}</div>
                        <div className="mt-2 space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Today:</span>
                            <span className={`font-medium ${
                              child.attendance_today === 'present' ? 'text-green-600' :
                              child.attendance_today === 'absent' ? 'text-red-600' :
                              'text-gray-500'
                            }`}>
                              {child.attendance_today === 'present' ? '✅ Present' :
                               child.attendance_today === 'absent' ? '❌ Absent' :
                               '❓ Unknown'}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Fees:</span>
                            <span className={`font-medium ${
                              child.fee_balance > 0 ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {child.fee_balance.toLocaleString()} UGX
                            </span>
                          </div>
                          {child.recent_grade && (
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Recent:</span>
                              <span className="font-medium text-blue-600">
                                {child.recent_grade.marks_obtained}/{child.recent_grade.max_marks} ({child.recent_grade.grade})
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Notifications */}
          {school.recent_notifications && school.recent_notifications.length > 0 && (
            <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Recent Notifications</h3>
              <div className="space-y-2">
                {school.recent_notifications.slice(0, 3).map((notif: any) => (
                  <div key={notif.id} className="text-sm">
                    <span className="font-medium text-gray-900">{notif.title}</span>
                    <span className="text-gray-600"> - {notif.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function SingleSchoolDashboard({ data, schoolId }: { data: any; schoolId: string }) {
  if (!data) return null;

  // This would show the regular single-school parent portal
  // For now, just show basic info
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Single School View
      </h2>
      <p className="text-gray-600">
        Showing data for school: {schoolId}
      </p>
      {/* Use existing ParentPortal component here */}
    </div>
  );
}
