import { Card, CardContent, Typography, Box } from '@mui/material';
import { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string;
  unit: string;
  icon: ReactNode;
  color: string;
}

export default function MetricCard({ title, value, unit, icon, color }: MetricCardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        border: `1px solid ${color}30`,
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Box sx={{ color, opacity: 0.8 }}>{icon}</Box>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, color }}>
          {value}
          <Typography component="span" variant="h6" sx={{ ml: 0.5, color: 'text.secondary' }}>
            {unit}
          </Typography>
        </Typography>
      </CardContent>
    </Card>
  );
}
