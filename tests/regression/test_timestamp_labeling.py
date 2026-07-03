from __future__ import annotations

from legal_research_skill.docx.render_model import DEFAULT_BUILD_EPOCH, RenderConfig


def test_render_config_default_created_at_is_the_documented_fixed_build_epoch():
    # ARCH-3 remediation: the default must stay a fixed, documented
    # constant (not datetime.now()), because independent CLI invocations of
    # the same input are required to produce byte-identical manifests and
    # DOCX output (see tests/acceptance/test_phase5_acceptance.py). This
    # test exists so that reintroducing a real-time default -- which would
    # silently reintroduce the underlying reproducibility bug this
    # remediation carefully avoided -- fails loudly here first.
    assert RenderConfig().created_at == DEFAULT_BUILD_EPOCH


def test_default_build_epoch_is_stable_across_independent_instances():
    # The constant must not be sourced from a clock: two independently
    # constructed RenderConfig() instances must agree, which is what makes
    # two independent CLI invocations of the same input byte-identical.
    assert RenderConfig().created_at == RenderConfig().created_at == DEFAULT_BUILD_EPOCH


def test_caller_can_override_with_a_real_timestamp():
    config = RenderConfig(created_at="2030-01-01T12:34:56Z")
    assert config.created_at == "2030-01-01T12:34:56Z"
