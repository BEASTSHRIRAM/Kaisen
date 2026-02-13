import { useEffect, useRef } from 'react';
import { Box, Typography, Card, CardContent, Chip } from '@mui/material';
import * as d3 from 'd3';
import { useStore } from '../../store/useStore';
import { GraphNode, GraphEdge } from '../../types';

export default function AttackGraphPage() {
  const svgRef = useRef<SVGSVGElement>(null);
  const { attackGraph } = useStore();

  useEffect(() => {
    if (!attackGraph || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Create simulation
    const simulation = d3
      .forceSimulation(attackGraph.nodes as any)
      .force(
        'link',
        d3
          .forceLink(attackGraph.edges)
          .id((d: any) => d.id)
          .distance(150)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Create arrow markers
    svg
      .append('defs')
      .selectAll('marker')
      .data(['normal', 'critical', 'warning'])
      .enter()
      .append('marker')
      .attr('id', (d) => `arrow-${d}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', (d) => (d === 'critical' ? '#f44336' : d === 'warning' ? '#ff9800' : '#00d4ff'));

    // Draw edges
    const link = g
      .append('g')
      .selectAll('line')
      .data(attackGraph.edges)
      .enter()
      .append('line')
      .attr('stroke', '#4a5568')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', (d: GraphEdge) => {
        const sourceNode = attackGraph.nodes.find((n) => n.id === d.source);
        if (sourceNode && sourceNode.anomaly_score > 0.7) return 'url(#arrow-critical)';
        if (sourceNode && sourceNode.anomaly_score > 0.5) return 'url(#arrow-warning)';
        return 'url(#arrow-normal)';
      });

    // Draw nodes
    const node = g
      .append('g')
      .selectAll('g')
      .data(attackGraph.nodes)
      .enter()
      .append('g')
      .call(
        d3
          .drag<any, GraphNode>()
          .on('start', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }) as any
      );

    // Node circles
    node
      .append('circle')
      .attr('r', (d) => {
        if (d.type === 'machine') return 25;
        if (d.type === 'external_ip') return 20;
        return 15;
      })
      .attr('fill', (d) => {
        if (d.anomaly_score > 0.7) return '#f44336';
        if (d.anomaly_score > 0.5) return '#ff9800';
        if (d.anomaly_score > 0.3) return '#ffeb3b';
        return '#4caf50';
      })
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');

    // Node icons (simplified)
    node
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('fill', '#ffffff')
      .attr('font-size', '14px')
      .text((d) => {
        if (d.type === 'machine') return '🖥️';
        if (d.type === 'external_ip') return '🌐';
        if (d.type === 'process') return '⚙️';
        if (d.type === 'service') return '📦';
        return '🔗';
      });

    // Node labels
    node
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 35)
      .attr('fill', '#ffffff')
      .attr('font-size', '10px')
      .text((d) => {
        const id = d.id.length > 15 ? d.id.substring(0, 12) + '...' : d.id;
        return id;
      });

    // Tooltips
    node.append('title').text((d) => {
      return `${d.type}\nID: ${d.id}\nAnomaly: ${d.anomaly_score.toFixed(2)}\nRisk: ${d.risk_score.toFixed(2)}`;
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [attackGraph]);

  const getNodeTypeCount = (type: string) => {
    return attackGraph?.nodes.filter((n) => n.type === type).length || 0;
  };

  const getHighRiskNodes = () => {
    return attackGraph?.nodes.filter((n) => n.anomaly_score > 0.7).length || 0;
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Attack Graph Visualization
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Chip label={`Machines: ${getNodeTypeCount('machine')}`} color="primary" />
        <Chip label={`External IPs: ${getNodeTypeCount('external_ip')}`} color="secondary" />
        <Chip label={`Processes: ${getNodeTypeCount('process')}`} color="info" />
        <Chip label={`High Risk Nodes: ${getHighRiskNodes()}`} color="error" />
        <Chip label={`Total Edges: ${attackGraph?.edges.length || 0}`} />
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#4caf50' }} />
              <Typography variant="body2">Normal (0-0.3)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#ffeb3b' }} />
              <Typography variant="body2">Low Risk (0.3-0.5)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#ff9800' }} />
              <Typography variant="body2">Medium Risk (0.5-0.7)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#f44336' }} />
              <Typography variant="body2">High Risk (0.7+)</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ height: 600 }}>
        <CardContent sx={{ height: '100%', p: 0 }}>
          {attackGraph && attackGraph.nodes.length > 0 ? (
            <svg ref={svgRef} style={{ width: '100%', height: '100%', background: '#0a0e27' }} />
          ) : (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography color="text.secondary">No graph data available</Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Drag nodes to reposition. Scroll to zoom. Click and drag background to pan.
      </Typography>
    </Box>
  );
}
