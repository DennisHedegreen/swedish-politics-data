import streamlit as st

from adapters import get_adapter
from core.runtime import resolve_requested_country_id, resolve_runtime_context
from core.styles import apply_global_styles
from country_registry import get_country_config, list_exposed_countries


def main():
    runtime_context = resolve_runtime_context(query_params=st.query_params)
    st.set_page_config(
        page_title=runtime_context.app_title,
        layout="wide",
        initial_sidebar_state="collapsed" if runtime_context.embedded_mode else "expanded",
    )
    apply_global_styles()

    country_configs = list_exposed_countries(
        runtime_context.requested_country_ids,
        allow_internal=runtime_context.profile.allow_internal,
    )
    country_configs = [
        config
        for config in country_configs
        if get_adapter(config.country_id).is_available(config, runtime_context)
    ]
    if not country_configs:
        st.error("No country data packs are currently exposed for this app profile.")
        st.stop()

    country_labels = {config.display_name: config.country_id for config in country_configs}
    requested_country = resolve_requested_country_id(
        country_labels.values(),
        requested_country_id=st.query_params.get("country"),
    )
    requested_country_label = next(
        label for label, country_id in country_labels.items() if country_id == requested_country
    )

    with st.sidebar:
        if len(country_labels) == 1:
            selected_country_label = requested_country_label
            st.markdown(
                "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.09em;text-transform:uppercase;color:#8888a0;margin-bottom:0.35rem;'>Country</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                (
                    "<div style='padding:0.62rem 0.8rem;border:1px solid #e0e0e8;border-radius:0.5rem;"
                    "background:#f7f7fb;color:#5a5a6a;font-size:0.88rem;line-height:1.3;'>"
                    f"{selected_country_label}</div>"
                ),
                unsafe_allow_html=True,
            )
        else:
            selected_country_label = st.selectbox(
                "Country",
                options=list(country_labels),
                index=list(country_labels).index(requested_country_label),
                key="country_switcher",
            )

    selected_country = country_labels[selected_country_label]
    if selected_country != requested_country:
        st.query_params["country"] = selected_country
        st.rerun()

    country_config = get_country_config(selected_country)
    adapter = get_adapter(selected_country)
    adapter.render(country_config, selected_country_label, runtime_context)


if __name__ == "__main__":
    main()
