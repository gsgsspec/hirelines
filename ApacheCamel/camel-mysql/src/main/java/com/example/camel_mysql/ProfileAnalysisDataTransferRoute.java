package com.example.camel_mysql;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
public class ProfileAnalysisDataTransferRoute extends RouteBuilder {

    @Override
    public void configure() {

        from("timer://profileAnalysisTimer?period=300000")
            .routeId("profile-analysis-aggregation-route")
            .log("================================================")
            .log("Starting Profile Analysis aggregation...")

            // 1️⃣ Aggregate profileactivity
            .to(
                "sql:SELECT " +
                "YEAR(datentime) AS year, " +
                "MONTH(datentime) AS month, " +
                "DAY(datentime) AS day, " +
                "acvityuserid AS userid, " +
                "companyid, " +
                "activitycode, " +
                "COUNT(DISTINCT profileid) AS profilescount " +
                "FROM profileactivity " +
                "WHERE datentime IS NOT NULL " +
                "AND acvityuserid IS NOT NULL " +
                "AND activitycode IS NOT NULL " +
                "GROUP BY YEAR(datentime), MONTH(datentime), DAY(datentime), companyid, acvityuserid, activitycode"
            )

            // 2️⃣ Split rows
            .split(body())
            .process(exchange -> {
                Map<String, Object> row =
                        exchange.getIn().getBody(Map.class);
                exchange.getIn().setHeaders(row);
            })

            // 3️⃣ Exists check
            .to(
                "sql:SELECT COUNT(*) AS exists_count " +
                "FROM profileanalysis " +
                "WHERE year = :#year " +
                "AND month = :#month " +
                "AND day = :#day " +
                "AND companyid = :#companyid " +
                "AND userid = :#userid " +
                "AND activitycode = :#activitycode"
            )

            .process(exchange -> {
                List<Map<String, Object>> result =
                        exchange.getIn().getBody(List.class);

                Number n = (Number) result.get(0).get("exists_count");
                exchange.getIn().setHeader(
                        "exists_count",
                        n != null ? n.intValue() : 0
                );
            })

            // 4️⃣ Update or Insert
            .choice()
                .when(simple("${header.exists_count} > 0"))
                    .log("Updating profileanalysis [${header.year}-${header.month}] user=${header.userid} code=${header.activitycode}")
                    .to(
                        "sql:UPDATE profileanalysis " +
                        "SET profilescount = :#profilescount " +
                        "WHERE year = :#year " +
                        "AND month = :#month " +
                        "AND day = :#day " +
                        "AND companyid = :#companyid " +
                        "AND userid = :#userid " +
                        "AND activitycode = :#activitycode"
                    )
                .otherwise()
                    .log("Inserting profileanalysis [${header.year}-${header.month}] user=${header.userid} code=${header.activitycode}")
                    .to(
                        "sql:INSERT INTO profileanalysis " +
                        "(year, month, day, companyid, userid, activitycode, profilescount) " +
                        "VALUES (:#year, :#month, :#day, :#companyid, :#userid, :#activitycode, :#profilescount)"
                    )
            .end()

            .log("Profile Analysis aggregation completed.")
            .log("================================================");
    }
}
