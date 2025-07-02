import { StatsCard } from '@/components/dashboard/StatsCard'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { MainNav } from '@/components/navigation/MainNav'

export default function DashboardPage() {
  return (
    <div className="flex flex-col">
      <MainNav />
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Total Clients"
            value="124"
            icon="users"
            description="+12 from last month"
          />
          <StatsCard
            title="Active Projects"
            value="24"
            icon="briefcase"
            description="+3 from last month"
          />
          <StatsCard
            title="Revenue"
            value="$12,345"
            icon="dollar"
            description="+8% from last month"
          />
          <StatsCard
            title="Pending Tasks"
            value="15"
            icon="list"
            description="+2 from yesterday"
          />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <div className="col-span-4">
            <RecentActivity />
          </div>
          <div className="col-span-3">
            <QuickActions />
          </div>
        </div>
      </div>
    </div>
  )
}