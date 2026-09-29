<?php

declare(strict_types=1);

namespace CarthageSoftware\ToolChainBenchmarks\Benchmark;

use CarthageSoftware\ToolChainBenchmarks\Configuration\Project;
use CarthageSoftware\ToolChainBenchmarks\Configuration\Tool;
use CarthageSoftware\ToolChainBenchmarks\Configuration\ToolInstance;
use CarthageSoftware\ToolChainBenchmarks\Configuration\ToolKind;
use CarthageSoftware\ToolChainBenchmarks\Support\Output;
use Psl\Iter;
use Psl\Vec;

/**
 * Records workloads excluded after repeated runner shutdowns.
 */
final readonly class ToolCoverage
{
    /**
     * @param list<ToolInstance> $tools
     */
    public static function warn(Project $project, array $tools): void
    {
        if (
            $project === Project::Magento
            && Iter\any($tools, static fn(ToolInstance $tool): bool => $tool->tool === Tool::Phan)
        ) {
            Output::warn('Phan is omitted on Magento after repeated hosted-runner shutdowns.');
        }
    }

    /**
     * @param list<ToolInstance> $tools
     * @return list<ToolInstance>
     */
    public static function select(Project $project, ToolKind $kind, array $tools): array
    {
        return Vec\filter(
            $tools,
            static fn(ToolInstance $tool): bool => (
                $tool->tool->getKind() === $kind
                && !($project === Project::Magento && $tool->tool === Tool::Phan)
            ),
        );
    }
}
