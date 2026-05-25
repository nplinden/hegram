window.statisticsTooltip = function (props) {
    var payload = props.payload;
    var label = props.label;
    var active = props.active;

    if (!active || !payload || !payload.length) return null;

    var total = payload.reduce(function (sum, entry) {
        return sum + (entry.value || 0);
    }, 0);

    var itemRows = payload.map(function (entry) {
        return React.createElement(
            "div",
            {
                key: entry.name,
                style: {
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "16px",
                    color: entry.color,
                },
            },
            [
                React.createElement("span", { key: "n" }, entry.name),
                React.createElement("span", { key: "v" }, entry.value.toLocaleString()),
            ]
        );
    });

    var totalRow = React.createElement(
        "div",
        {
            key: "total",
            style: {
                display: "flex",
                justifyContent: "space-between",
                gap: "16px",
                borderTop: "1px solid #dee2e6",
                marginTop: "4px",
                paddingTop: "4px",
                fontWeight: 600,
                color: "#000",
            },
        },
        [
            React.createElement("span", { key: "n" }, "Total"),
            React.createElement("span", { key: "v" }, total.toLocaleString()),
        ]
    );

    return React.createElement(
        "div",
        {
            style: {
                background: "white",
                border: "1px solid #dee2e6",
                borderRadius: "4px",
                padding: "8px 12px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
                fontSize: "12px",
            },
        },
        [
            React.createElement(
                "div",
                { key: "label", style: { fontWeight: 700, marginBottom: "6px", fontSize: "13px" } },
                label
            ),
            ...itemRows,
            totalRow,
        ]
    );
};
