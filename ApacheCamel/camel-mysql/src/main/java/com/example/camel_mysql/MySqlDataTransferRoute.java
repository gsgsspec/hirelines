package com.example.camel_mysql;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.component.sql.SqlComponent;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;

import java.util.Map;
import java.util.List;

@Component
public class MySqlDataTransferRoute extends RouteBuilder {

    private final DataSource dataSource;

    public MySqlDataTransferRoute(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void configure() throws Exception {

        // Set up SQL Component for Camel

        SqlComponent sqlComponent = new SqlComponent();
        sqlComponent.setDataSource(dataSource);
        getContext().addComponent("sql", sqlComponent);

        from("timer://foo?period=5000")

                .to("sql:SELECT type, COUNT(*) AS count FROM people GROUP BY type")
                .split(body())
                .process(exchange -> {

                    Map<String, Object> row = exchange.getIn().getBody(Map.class);
                    String type = (String) row.get("type");
                    Long count = ((Number) row.get("count")).longValue();

                    exchange.getIn().setHeader("type", type);
                    exchange.getIn().setHeader("count", count);
                    
                })
                // Step 2: Check if the type exists in the 'datatable' table

                .to("sql:SELECT COUNT(*) AS exists_count FROM datatable WHERE type = :#type")

                .process(exchange -> {
                    // Extract the existence count from the result

                    List<Map<String, Object>> result = exchange.getIn().getBody(List.class);

                    Integer existsCount = ((Number) result.get(0).get("exists_count")).intValue();

                    // Set the existence count as a header
                    exchange.getIn().setHeader("exists_count", existsCount);
                })
                .choice()
                // If type exists, update the count
                .when(simple("${header.exists_count} > 0"))
                .log("Updating count for existing type: ${header.type}")
                .to("sql:UPDATE datatable SET count = :#count WHERE type = :#type")

                // If type does not exist, insert a new row
                .otherwise()
                .log("Inserting new type: ${header.type} with count: ${header.count}")
                .to("sql:INSERT INTO datatable (type, count) VALUES (:#type, :#count)")
                .end()
                .to("log:completed");

    }
}
