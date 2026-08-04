'use client';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color?: string;
}

export function StatCard({ title, value, icon, color = 'blue' }: StatCardProps) {
  return (
    <div className="group relative">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-600 to-purple-600 rounded-xl opacity-0 group-hover:opacity-20 blur transition duration-1000 group-hover:duration-200"></div>
      <div className={`relative bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm font-medium uppercase tracking-wide">{title}</p>
            <p className={`text-3xl font-bold mt-3 bg-gradient-to-r ${getGradient(color)} bg-clip-text text-transparent`}>
              {value}
            </p>
          </div>
          <div className="text-4xl transform group-hover:scale-110 transition-transform duration-300">{icon}</div>
        </div>
      </div>
    </div>
  );
}

function getGradient(color: string): string {
  const gradients: Record<string, string> = {
    blue: 'from-blue-600 to-blue-400',
    green: 'from-green-600 to-green-400',
    purple: 'from-purple-600 to-purple-400',
    red: 'from-red-600 to-red-400',
  };
  return gradients[color] || gradients.blue;
}
